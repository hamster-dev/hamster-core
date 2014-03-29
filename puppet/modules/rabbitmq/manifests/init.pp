class rabbitmq {
    package { 'rabbitmq-server': ensure => latest }

    service { 'rabbitmq-server':
        ensure    => true,
        enable    => true,
        subscribe => [ Package[rabbitmq-server] ],
    }
}
