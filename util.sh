check_up() {
	# Verify that a service is running
    service=$1
    host=$2
    port=$3
    max=5
    counter=1

    while true; do
        python -c "import socket;s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);s.connect(('$host', $port))" \
            >/dev/null 2>/dev/null && break || \
            echo "Waiting for ${service}@${host}:${port} to start" \
            "[`expr ${max} - ${counter}`] ..."
        if [ ${counter} == ${max} ];then
            echo "Error connecting to ${service}."
            exit 1
        fi
        sleep 5
        (( counter++ ))
    done
}

develop_pkgs() {
    # install all python packages in app dir
    if [[ ! -z $HAMSTER_DEVELOP ]]; then
        echo "installing pkgs"
        for f in `find . -mindepth 2 -type f -name setup.py`; do
            pkg=$(basename `dirname $f`)
            pip freeze |grep -i "^$pkg=" >/dev/null && pip uninstall -y $pkg
            find $pkg -type d -name "__pycache__" |rm -rf {}\;
            pip install -e $pkg
        done
    fi
}
