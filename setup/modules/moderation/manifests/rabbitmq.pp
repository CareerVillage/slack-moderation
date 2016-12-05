class moderation::rabbitmq {

    package { "rabbitmq-server": } ->

    exec { "moderation::rabbitmq::admin":
        command => "/usr/lib/rabbitmq/lib/rabbitmq_server-2.7.1/sbin/rabbitmq-plugins enable rabbitmq_management",
        notify  => Service["rabbitmq-server"],
        refreshonly => true;
    }

    service { "rabbitmq-server":
        ensure      => "running",
        enable      => true,
        require     => Package["rabbitmq-server"];
    }

}