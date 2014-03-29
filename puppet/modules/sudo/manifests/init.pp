class sudo {
    package { 'sudo': ensure => latest, require => Class[apt] }

    file { 'sudoers':
        path    => '/etc/sudoers',
        owner   => 'root',
        group   => 'root',
        mode    => '0440',
        source  => 'puppet:///modules/sudo/sudoers',
        require => Package['sudo'],
    }
}
