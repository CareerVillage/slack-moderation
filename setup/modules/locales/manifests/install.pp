class locales::install inherits locales {

  package { $::locales::package_name:
    ensure => present,
  }
}