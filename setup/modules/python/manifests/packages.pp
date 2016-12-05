class python::packages {

    $packages = ["python-dev", "python-virtualenv"]

    package { $packages:
        ensure => present;
    }

}