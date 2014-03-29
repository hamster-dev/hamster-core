class packages::debian {
    package { 'rsync':       ensure => latest }
    package { 'lsof':        ensure => latest }
    package { 'dstat':       ensure => latest }
    package { 'wget':        ensure => latest }
    package { 'traceroute':  ensure => latest }
    package { 'bash':        ensure => latest }
    package { 'ethtool':     ensure => latest }
    package { 'vim':         ensure => latest }
    package { 'vim-tiny':    ensure => absent }
}
