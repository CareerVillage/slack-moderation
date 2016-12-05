define python::venv ($requirements, $user, $group) {

    $checksum = "${name}/requirements.checksum"

    Exec {
        path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        user => $user,
        group => $group
    }

    include python::packages

    exec { "python::venv ${name}":
        command => "/usr/bin/virtualenv ${name} --no-site-packages --distribute",
        creates => $name,
        notify => Exec["python::venv $name update"],
        require => Class["python::packages"];
    }

    exec { "python::venv ${name} update":
        command => "${name}/bin/pip install -U distribute",
        refreshonly => true;
    }

    if $requirements {

        exec { "python::venv ${name} checksum":
            command => "/usr/bin/sha1sum ${requirements} > $checksum",
            refreshonly => true;
        }

        exec { "python::venv ${name} install":
            command => "${name}/bin/pip install -r ${requirements}",
            cwd => $name,
            timeout => 3600,
            unless => "/usr/bin/sha1sum -c ${checksum}",
            notify => Exec["python::venv ${name} checksum"],
            require => Exec["python::venv ${name} update"],
            logoutput => "on_failure";
        }

    }

}
