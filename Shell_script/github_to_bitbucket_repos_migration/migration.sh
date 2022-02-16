#!/bin/bash
set -e
rootdir=`pwd`
echo $rootdir
source auth.config

echo $stash_username

count=`cat repos.config | wc -l`

echo $count

for (( c=1; c<=$count; c++ ))
do
   echo "C=$c"
   cd $rootdir
   line1=`cat repos.config | head -$c | tail -1 | awk -F"," '{print \$1}'`
   export "$line1"
   echo "Source Repo $source_repo"
   string1=`echo $source_repo | awk -F'//' '{print $2}'`
   echo $string1
   source_url_with_creds="https://$github_username:$github_pass@$string1"
   #echo $source_url_with_creds

   ##rm -rf lab_dir
   mkdir -p lab_dir
   project_name=`echo $source_repo | awk -F"/" '{print $NF}' | awk -F"." '{print $1}'`
   cd lab_dir
   git clone $source_url_with_creds
   cd $project_name
   set +e
   git branch -r | grep -v '\->' | while read remote; do git branch --track "${remote#origin/}" "$remote"; done
   set -e
   git fetch --all --tags

   cd $rootdir
   line2=`cat repos.config | head -$c | tail -1 | awk -F"," '{print \$2}'`
   export "$line2"
   echo "Destination Repo $destination_repo"
   string2=`echo $destination_repo | awk -F'//' '{print $2}'`
   echo $string2
   destination_url_with_creds="https://$stash_username:$stash_pass@$string2"
   #echo $destination_url_with_creds

   cd lab_dir/$project_name
   git remote set-url origin $destination_url_with_creds

   git push --all #--tags
   git push --tags

   cd ../..
   rm -rf lab_dir/$project_name

done
