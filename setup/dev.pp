class dev {

    $target = "dev"
    $root_dir = "/home/vagrant/moderation"
    $user = "vagrant"
    $group = "vagrant"

    host {
        "moderation.moderation.db":
            ip => "127.0.0.1";
    }

    class { "moderation":
        target => $target,
        root_dir => $root_dir,
        user => $user,
        group => $group;
    }

    class { "moderation::app::site":
        role => "dev";
    }

    class { "moderation::app::deploy":
        role => "master";
    }

    class { "moderation::app::db": }

    class { "moderation::cache": }

    class { "moderation::rabbitmq": }

}

class { "dev": }
