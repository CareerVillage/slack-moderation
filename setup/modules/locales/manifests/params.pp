class locales::params {
  $available      = ['en_US.UTF-8 UTF-8']
  $default_value  = 'en_US.UTF-8'
  $package_ensure = present
  $package_name   = 'locales'
  case $::osfamily {
    'Debian': {
      case $::operatingsystem {
        ubuntu: {
          case $::lsbdistcodename {
            xenial: { $localegenfile = '/etc/locale.gen' }
            default: { $localegenfile = '/var/lib/locales/supported.d/local' }
          }
        }
        default: { $localegenfile = '/etc/locale.gen' }
      }
    }
    default: {
      fail("Unsupported osfamily: ${::osfamily}, module ${module_name} only supports the Debian osfamily.")
    }
  }
}