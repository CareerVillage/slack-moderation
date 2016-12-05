class moderation::logging::site {

    $sentry_dir = "${moderation::extras_dir}/sentry"
    $sentry_source = "${sentry_dir}/source"
    $sentry_venv = "${sentry_dir}/venv"

    include nginx
    include supervisor

    nginx::vhost { "moderation::logging::site":
        name    => "moderation_logging",
        content => template("${module_name}/logging/nginx.conf"),
        require => [Class["moderation"], Class["nginx"]];
    }

    file {
        $sentry_dir:
            owner  => $moderation::user,
            group  => $moderation::group,
            ensure => directory;
        $sentry_source:
            owner   => $moderation::user,
            group   => $moderation::group,
            ensure  => directory,
            require => File[$sentry_dir];
        "${sentry_source}/requirements.pip":
            ensure  => file,
            source  => "puppet:///modules/${module_name}/logging/requirements.pip",
            require => File[$sentry_source];
        "${sentry_source}/settings.py":
            ensure  => file,
            content => template("${module_name}/logging/settings.py.erb"),
            notify  => Service["supervisor"],
            require => File[$sentry_source];
        "${sentry_source}/sentry.json":
            ensure  => file,
            source  => "puppet:///modules/${module_name}/logging/fixture.json",
            require => File[$sentry_source];
    }

    python::venv { $sentry_venv:
        requirements => "${sentry_source}/requirements.pip",
        user         => $moderation::user,
        group        => $moderation::group,
        require      => [Class["moderation"], File["${sentry_source}/requirements.pip"]];
    }

    exec { "sentry --config=settings.py loaddata sentry.json":
        path    => "${sentry_venv}/bin",
        cwd     => "${sentry_source}",
        require => [Python::Venv[$sentry_venv], File["${sentry_source}/sentry.json"]];
    }

    supervisor::app { "logging_site":
        command     => "${sentry_venv}/bin/sentry --config=settings.py start",
        directory   => "${sentry_source}",
        environment => "PATH=\"${sentry_venv}/bin\"",
        user        => $moderation::user,
        require     => Python::Venv[$sentry_venv],
        stdout_logfile => "${moderation::log_dir}/logging_site_stdout.log",
        stderr_logfile => "${moderation::log_dir}/logging_site_stderr.log";
    }

    exec { "logging_site_restart":
         command => "/usr/bin/supervisorctl restart logging_site",
         require => Supervisor::App["logging_site"];
    }

}