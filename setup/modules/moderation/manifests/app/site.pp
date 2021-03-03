class moderation::app::site ($role) {

    include moderation::venv
    include nginx
    include supervisor

    # If /etc/ntp.conf does not exist. Execute the command.
    exec { "moderation::app::site::ensure_ntp_update_time":
        command => "ntpdate pool.ntp.org",
        path    => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        creates => "/etc/ntp.conf",
        require => Package["ntp"];
    }

    if $moderation::target == 'pro' {

        file { "${moderation::extras_dir}/send_stats_to_gspread.sh":
            owner   => $user,
            group   => $group,
            mode    => "755",
            content => template("${module_name}/app/send_stats_to_gspread.sh.erb"),
            require => Class["moderation"];
        }

        cron { "moderation::app::site::send_stats_to_gspread":
            command => "${moderation::extras_dir}/send_stats_to_gspread.sh",
            user    => $user,
            hour    => 1, # 5pm (1 UTC)
            minute  => 00,
            weekday => 1,
            require => File["${moderation::extras_dir}/send_stats_to_gspread.sh"];
        }
    }
    
    if $moderation::target != 'dev' {
        file {
            "${moderation::data_dir}/moderation_ssl_key":
                owner   => $user,
                group   => $group,
                mode    => '644',
                ensure  => present,
                source  => "/tmp/moderation_ssl_key";
            "${moderation::data_dir}/moderation_ssl_crt":
                owner   => $user,
                group   => $group,
                ensure  => present,
                mode    => '644',
                source  => "/tmp/moderation_ssl_crt";
        }
    }


    nginx::vhost { "moderation::moderation::site":
        name    => "moderation_moderation",
        content => template("${module_name}/app/nginx.conf"),
        require => [Class["moderation"], Class["nginx"]];
    }

    if $moderation::target != 'dev' {

        include uwsgi

        if $moderation::target in ['local', 'sta'] {

            if $moderation::target == 'local' {
                $settings = 'local'
            } elsif $moderation::target == 'sta' {
                $settings = 'staging'
            }

            supervisor::app { "moderation_app_site":
                command     => "/usr/local/bin/uwsgi
                                        --socket=${moderation::run_dir}/app_uwsgi.sock
                                        --chmod-socket=666
                                        --processes=16
                                        --harakiri=120
                                        --max-requests=5000
                                        --enable-threads
                                        --single-interpreter
                                        --master
                                        --vacuum
                                        --virtualenv=${moderation::venv_dir}
                                        --pp=${moderation::app_dir}
                                        --module=moderation.wsgi:application",
                environment => "DJANGO_SETTINGS_MODULE='moderation.settings'",
                user        => $moderation::user,
                require     => [Class["moderation::venv"],
                                Class["moderation"],
                                Class["moderation::app::deploy"]],
                stdout_logfile => "${moderation::log_dir}/app_stdout.log",
                stderr_logfile => "${moderation::log_dir}/app_stderr.log";
            }

            exec { "app_restart":
                 command => "/usr/bin/supervisorctl restart moderation_app_site",
                 require => Supervisor::App["moderation_app_site"];
            }

        } else {

            if $moderation::target == 'pro' {
              $settings = 'production'
            } elsif $moderation::target == 'sta' {
              $settings = 'staging'
            }
            supervisor::app { "app_site":
                command     => "/usr/local/bin/uwsgi
                                        --socket=${moderation::run_dir}/app_uwsgi.sock
                                        --chmod-socket=666
                                        --processes=4
                                        --harakiri=120
                                        --max-requests=5000
                                        --master
                                        --vacuum
                                        --virtualenv=${moderation::venv_dir}
                                        --pp=${moderation::app_dir}
                                        --module=moderation.wsgi:application",

                environment => "DJANGO_SETTINGS_MODULE='moderation.settings.${settings}'",
                user        => $moderation::user,
                require     => [Class["moderation::app::deploy"]],
                stdout_logfile => "${moderation::log_dir}/app_site_stdout.log",
                stderr_logfile => "${moderation::log_dir}/app_site_stderr.log";
            }

            exec { "app_site_restart":
                 command => "/usr/bin/supervisorctl restart app_site",
                 require => Supervisor::App["app_site"];
            }

        }

        if $moderation::target == 'local' {

            supervisor::app { "moderation_site":
                command     => "/usr/local/bin/uwsgi
                                        --socket=${moderation::run_dir}/moderation_uwsgi.sock
                                        --buffer-size=8192
                                        --chmod-socket=666
                                        --processes=2
                                        --harakiri=120
                                        --max-requests=5000
                                        --master
                                        --vacuum
                                        --virtualenv=${moderation::venv_dir}
                                        --pp=${moderation::app_dir}
                                        --module=moderation.wsgi:application",

                environment => "DJANGO_SETTINGS_MODULE='moderation.settings'",
                user        => $moderation::user,
                require     => [Class["moderation::venv"],
                                Class["moderation"],
                                Class["moderation::app::deploy"]],
                stdout_logfile => "${moderation::log_dir}/moderation_site_stdout.log",
                stderr_logfile => "${moderation::log_dir}/moderation_site_stderr.log";
            }

            exec { "moderation_site_restart":
                 command => "/usr/bin/supervisorctl restart moderation_site",
                 require => Supervisor::App["moderation_site"];
            }

        } else {


            supervisor::app { "moderation_site":
                command     => "/usr/local/bin/uwsgi
                                        --socket=${moderation::run_dir}/moderation_uwsgi.sock
                                        --buffer-size=8192
                                        --chmod-socket=666
                                        --processes=2
                                        --harakiri=120
                                        --max-requests=5000
                                        --master
                                        --vacuum
                                        --virtualenv=${moderation::venv_dir}
                                        --pp=${moderation::app_dir}
                                        --module=moderation.wsgi:application",

                environment => "DJANGO_SETTINGS_MODULE='moderation.settings'",
                user        => $moderation::user,
                require     => Class["moderation::app::deploy"],
                stdout_logfile => "${moderation::log_dir}/moderation_site_stdout.log",
                stderr_logfile => "${moderation::log_dir}/moderation_site_stderr.log";
            }

            exec { "moderation_site_restart":
                 command => "/usr/bin/supervisorctl restart moderation_site",
                 require => Supervisor::App["moderation_site"];
            }

        }
    }

}
