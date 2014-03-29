class packages::alternatives {
    $vim = '/usr/bin/vim.basic'
    $rle = '$(readlink /etc/alternatives/editor)'

    exec {
        "/usr/bin/update-alternatives --set editor $vim":
            unless  => "/usr/bin/test $rle == $vim",
            require => Package['vim'];
    }
}
