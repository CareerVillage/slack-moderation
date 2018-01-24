class moderation::code ($user, $group, $source_dir) {

    $git_repo   = "${::moderation_git_repo}"
    $git_key = "moderation_git"

    file {
        "/home/${user}/.ssh":
            owner  => $user,
            group  => $group,
            ensure => directory;
        "/home/${user}/.ssh/${git_key}":
            owner   => $user,
            group   => $group,
            mode    => '600',
            ensure  => present,
            source  => "/tmp/moderation_git_key",
            require => File["/home/${user}/.ssh"];
        "/home/${user}/.ssh/${git_key}.pub":
            owner   => $user,
            group   => $group,
            ensure  => present,
            source  => "/tmp/moderation_git_pub",
            require => File["/home/${user}/.ssh"];
    }

    vcsrepo { 'source':
        ensure   => latest,
        provider => git,
        source   => "${git_repo}",
        revision => "master",
        owner    => $user,
        user     => $user,
        group    => $group,
        path     => $source_dir,
        identity => "/home/${user}/.ssh/${git_key}",
        require  => File["/home/$user/.ssh/${git_key}"];
    }

}