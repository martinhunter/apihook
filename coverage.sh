help_msg="help:\n
  bash coverage.sh install  # install requirement\n
  bash coverage.sh init  # install coverage tools\n
  bash coverage.sh report  # test and report in cmdline\n
  bash coverage.sh html  # test and save result in folder covhtml\n
"
function pip_install() {
  packs=$(python -m pip freeze | awk -F '==' '{print $1}')
  for pack in $@
  do
    found=0
    for installed in ${packs[@]}
    do
      if [[ $installed == $pack ]];then
        found=1
        break
      fi
    done
    if [[ $found == 1 ]];then
      echo "$pack already installed"
    else
      python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple $pack
    fi
  done
}

function test_all() {
  folder=$(pwd)/test
  for file in $(ls $folder)
  do
    if [[ $file =~ ^test_* ]];then
      echo ~~~TESTING: ${file} ~~~
#      --concurrency gevent  # add this option if await code is not covered
      python -m coverage run -p --include=./*.py ${folder}/${file}
    fi
  done
  python -m coverage combine
}

# run shell
if [[ $1 == "install" ]];then
  python -m pip install  -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirement.txt
elif [[ $1 == "init" ]];then
  pip_install coverage
elif [[ $1 == "report" ]];then
  test_all
  python -m coverage report -m
elif [[ $1 == "html" ]];then
  test_all
  python -m coverage html -d covhtml
else
  echo -e $help_msg
fi


