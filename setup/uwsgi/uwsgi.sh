#!/bin/sh -e

DIRNAME=`dirname $0`
cd $DIRNAME
USAGE="$0 [ --update ]"
if [ `id -u` != 0 ]; then
echo 'You must be root to run this script'
exit 1
fi

if [ $# -eq 1 ]; then
	if [ "$1" = "--update" ] ; then
		time=`ls -l --time-style="+%x %X" uwsgi.te | awk '{ printf "%s %s", $6, $7 }'`
		rules=`ausearch --start $time -m avc --raw -se uwsgi`
		if [ x"$rules" != "x" ] ; then
			echo "Found avc's to update policy with"
			echo -e "$rules" | audit2allow -R
			echo "Do you want these changes added to policy [y/n]?"
			read ANS
			if [ "$ANS" = "y" -o "$ANS" = "Y" ] ; then
				echo "Updating policy"
				echo -e "$rules" | audit2allow -R >> uwsgi.te
				# Fall though and rebuild policy
			else
				exit 0
			fi
		else
			echo "No new avcs found"
			exit 0
		fi
	else
		echo -e $USAGE
		exit 1
	fi
elif [ $# -ge 2 ] ; then
	echo -e $USAGE
	exit 1
fi

echo "Building and Loading Policy"
set -x
make -f /usr/share/selinux/devel/Makefile uwsgi.pp || exit
/usr/sbin/semodule -i uwsgi.pp

# Generate a man page of the installed module
sepolicy manpage -p . -d uwsgi_t
# Fixing the file context on /var/lib/flask/.cache/pypoetry/virtualenvs/therm-flask-oT0ltQ80-py3.13/bin/uwsgi
/sbin/restorecon -F -R -v /var/lib/flask/.cache/pypoetry/virtualenvs/therm-flask-oT0ltQ80-py3.13/bin/uwsgi
# Fixing the file context on /var/run/uwsgi
/sbin/restorecon -F -R -v /var/run/uwsgi
# Fixing the file context on /var/log/uwsgi
/sbin/restorecon -F -R -v /var/log/uwsgi
# Generate a rpm package for the newly generated policy

pwd=$(pwd)
rpmbuild --define "_sourcedir ${pwd}" --define "_specdir ${pwd}" --define "_builddir ${pwd}" --define "_srcrpmdir ${pwd}" --define "_rpmdir ${pwd}" --define "_buildrootdir ${pwd}/.build"  -ba uwsgi_selinux.spec
