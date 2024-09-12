#!/bin/bash

containers=($(docker ps -q | xargs -I ARGS docker inspect ARGS --format '{{.Name}}'|sed 's/\///g'))

list=(solr72-jobs-backfill solr45-requests solr45-trial-requests solr45-tasks solr45-geo solr45-accounts-notes solr45-accounts solr45-account-requests solr72-candidates solr72-trial-searches solr72-salaries solr72-jobtitles solr72-companies solr72-builder-dict solr72-addresses solr72-jobs)

for l in ${list[@]}
  do
    match=""
    for c in ${containers[@]}
      do
        if [[ ${l} == ${c} ]]; then
           match=$c
	   break
        fi
    done
    if [[ ${match} ]]; then
      echo "${match} matches to the list ${l}"
    else
      echo "${c} does not match"
   fi  
 
  done
