define moderation::user ($ensure=present, $groups=[], $key=undef) {

  $user = $name

  user { $user:
    ensure     => $ensure,
    groups     => $groups,
    home       => "/home/$user",
    managehome => true,
    shell      => '/bin/bash';
  }

  if $ensure == absent {
    file { "/home/$user":
      ensure  => absent,
      recurse => true,
      force   => true,
      purge   => true,
      require => User[$user];
    }
  }

  if $ensure == present and $key {

    file { "/home/$user/.ssh":
      ensure  => directory,
      mode    => 755,
      owner   => $user,
      group   => $user,
      require => User[$user];
    }

    file { "/home/$user/.ssh/authorized_keys":
      ensure  => present,
      mode    => 644,
      owner   => $user,
      group   => $user,
      content => $key,
      require => File["/home/$user/.ssh"];
    }

  }

}