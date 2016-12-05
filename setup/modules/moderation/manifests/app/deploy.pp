class moderation::app::deploy ($role) {

    include supervisor
    include moderation::venv

    if $moderation::target != 'dev' {

        file { "${moderation::app_dir}/moderation/settings/secrets.py":
            owner   => $moderation::user,
            group   => $moderation::group,
            ensure  => present,
            content => template("${module_name}/app/secrets.py.erb"),
            require => Vcsrepo['source'];
        }

        file { "${moderation::app_dir}/moderation/settings/local.py":
            owner   => $moderation::user,
            group   => $moderation::group,
            ensure  => present,
            content => template("${module_name}/app/local.py.erb"),
            require => Vcsrepo['source'];
        }

        if $moderation::target != 'pro' and $::moderation_reset_db == 'true' and $role == 'master' {
            exec { 'moderation::app::deploy::db':
                command   => "python manage.py reset_db --traceback",
                cwd       => $moderation::app_dir,
                user      => $moderation::user,
                group     => $moderation::group,
                path      => "${moderation::venv_dir}/bin",
                logoutput => "on_failure",
                require   => [Postgresql::Database_grant["moderation-all"],
                            File["${moderation::app_dir}/moderation/settings/secrets.py"],
                            Class["moderation::venv"]];
            }
        }

        if $role == 'master' {

            exec { 'moderation::app::deploy::collectstatic':
                command   => "python manage.py collectstatic --noinput",
                cwd       => $moderation::app_dir,
                user      => $moderation::user,
                group     => $moderation::group,
                path      => "${moderation::venv_dir}/bin",
                logoutput => "on_failure",
                require   => [File["${moderation::app_dir}/moderation/settings/secrets.py"],
                              Class["moderation::venv"]];
            }

        }

        supervisor::app { "moderation_celery":
            command     => "python manage.py celery worker --loglevel=info",
            directory   => $moderation::app_dir,
            environment => "PATH=\"${moderation::venv_dir}/bin\"",
            user        => $moderation::user,
            stdout_logfile => "${moderation::log_dir}/moderation_celery_supervisor_stdout.log",
            stderr_logfile => "${moderation::log_dir}/moderation_celery_supervisor_stderr.log";
        }

        exec { "cvmoderation_celery_restart":
             command => "/usr/bin/supervisorctl restart moderationqueue_celery",
             require => Supervisor::App["moderation_celery"];
        }

        if $role == 'master' {


        }

    }

    if $moderation::target == 'dev' {
        file { "${moderation::app_dir}/moderation/settings/secrets.py":
            owner   => $moderation::user,
            group   => $moderation::group,
            ensure  => present,
            content => template("${module_name}/app/secrets.py.erb");
        }

        file { "${moderation::app_dir}/moderation/settings/local.py":
            owner   => $moderation::user,
            group   => $moderation::group,
            ensure  => present,
            content => template("${module_name}/app/local.py.erb");
        }
    }

    if $role == 'master' {

        exec { 'moderation::app::deploy::db':
            command   => "python manage.py migrate --noinput --traceback",
            cwd       => $moderation::app_dir,
            user      => $moderation::user,
            group     => $moderation::group,
            path      => "${moderation::venv_dir}/bin",
            logoutput => "on_failure",
            require   => [File["${moderation::app_dir}/moderation/settings/secrets.py"],
                        Class["moderation::venv"], Class["moderation::app::db"]];
        }
    }

}
