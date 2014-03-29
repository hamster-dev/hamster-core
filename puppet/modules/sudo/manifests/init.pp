class sudo {
    package { 'sudo': ensure => latest }

    file { 'sudoers':
        path    => '/etc/sudoers',
        owner   => 'root',
        group   => 'root',
        mode    => '0440',
        source  => 'puppet:///modules/sudo/sudoers',
        require => Package['sudo'],
    }
}
