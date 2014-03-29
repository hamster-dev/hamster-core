class ntp {
    package { 'ntp': ensure => latest }

    file { 'ntp-conf':
        path    => '/etc/ntp.conf',
        owner   => 'root',
        group   => 'root',
        mode    => '0644',
        source  => 'puppet:///modules/ntp/ntp-conf',
        require => Package['ntp'],
    }

    service { 'ntp':
        ensure    => true,
        enable    => true,
        subscribe => [ File['ntp-conf'], Package [ntp] ],
    }
}
