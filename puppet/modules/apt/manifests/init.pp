class apt {
    package { apt: ensure => latest }

    exec { 'apt-update':
        command     => '/usr/bin/apt-get update',
        refreshonly => true;
    }

    file {
        'apt-conf':
            path    => '/etc/apt/apt.conf',
            owner   => 'root',
            group   => 'root',
            mode    => 0644,
            source  => 'puppet:///modules/apt/apt-conf',
            require => Package['apt'];
        'apt-sources':
            path    => '/etc/apt/sources.list',
            owner   => 'root',
            group   => 'root',
            mode    => 0644,
            source  => 'puppet:///modules/apt/sources-list',
            require => Package['apt'],
            notify  => Exec['apt-update'];
    }
}

define apt::key($keyid, $ensure, $keyserver = 'keyserver.ubuntu.com') {
  case $ensure {
    present: {
      exec { 'Import $keyid to apt keystore':
        path        => '/bin:/usr/bin',
        environment => 'HOME=/root',
        command     => "gpg --keyserver $keyserver --recv-keys $keyid && gpg --export --armor $keyid | apt-key add -",
        user        => 'root',
        group       => 'root',
        unless      => "apt-key list | grep $keyid",
        logoutput   => on_failure,
      }
    }
    absent:  {
      exec { 'Remove $keyid from apt keystore':
        path        => '/bin:/usr/bin',
        environment => 'HOME=/root',
        command     => "apt-key del $keyid",
        user        => 'root',
        group       => 'root',
        onlyif      => "apt-key list | grep $keyid",
      }
    }
    default: {
      fail "Invalid 'ensure' value '$ensure' for apt::key"
    }
  }
}
