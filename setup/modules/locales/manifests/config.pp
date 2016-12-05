class locales::config inherits locales {
  file { $::locales::localegenfile:
    content => inline_template('<%= @available.join("\n") + "\n" %>'),
  }

  file { '/etc/default/locale':
    content => template('locales/default_locales.erb')
  }

  exec { '/usr/sbin/locale-gen':
    subscribe   => [File[$::locales::localegenfile], File['/etc/default/locale']],
    refreshonly => true,
  }

  exec { '/usr/sbin/update-locale':
    subscribe   => [File[$::locales::localegenfile], File['/etc/default/locale']],
    refreshonly => true,
  }
}