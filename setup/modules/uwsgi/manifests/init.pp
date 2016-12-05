class uwsgi {

  exec { "uwsgi":

      path    => "/usr/local/bin:/usr/bin:/bin",
      command => "pip install http://projects.unbit.it/downloads/uwsgi-1.9.13.tar.gz",
      user    => "root",
      creates => "/usr/local/bin/uwsgi",
      require => Package["python-pip"];

  }

}
