class supervisor {

  package { "supervisor":
    ensure => installed;
  }

  service { "supervisor":
    ensure  => running,
    enable  => true,
    require => Package["supervisor"],
    stop    => "service supervisor stop",
    start   => "service supervisor start",
    restart => "supervisorctl update";
  }

  file { "/etc/supervisor/conf.d/":
    ensure  => directory,
    recurse => true,
    purge   => true,
    notify  => Service["supervisor"],
    require => Package["supervisor"];
  }
}
