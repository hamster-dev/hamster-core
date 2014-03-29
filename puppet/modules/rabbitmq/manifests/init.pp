class rabbitmq {
    package { 'rabbitmq-server': ensure => latest }

    service { 'rabbitmq-server':
        ensure    => true,
        enable    => true,
        subscribe => [ Package[rabbitmq-server], Exec[enable_rabbitmq_management] ],
    }

    exec { 'enable_rabbitmq_management':
        command     => "/usr/sbin/rabbitmq-plugins enable rabbitmq_management",
        environment => "HOME=/root",
        unless      => "/bin/grep rabbitmq_management /etc/rabbitmq/enabled_plugins",
    }
}
