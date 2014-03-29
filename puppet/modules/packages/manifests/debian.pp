class packages::debian {
    package { 'rsync':             ensure => latest, require => Class[apt] }
    package { 'lsof':              ensure => latest, require => Class[apt] }
    package { 'dstat':             ensure => latest, require => Class[apt] }
    package { 'wget':              ensure => latest, require => Class[apt] }
    package { 'traceroute':        ensure => latest, require => Class[apt] }
    package { 'bash':              ensure => latest, require => Class[apt] }
    package { 'ethtool':           ensure => latest, require => Class[apt] }
    package { 'vim':               ensure => latest, require => Class[apt] }
    package { 'git':               ensure => latest, require => Class[apt] }
    package { 'python-virtualenv': ensure => latest, require => Class[apt] }
    package { 'virtualenvwrapper': ensure => latest, require => Class[apt] }
    package { 'vim-tiny':          ensure => absent }
}
