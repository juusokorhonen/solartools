# solartools
Tools for solving solar energy problems.

## Installation

### Install python2.7
    $ brew install python

### Install pip
    $ easy_install pip

### Install virtualenv and virtualenvwrapper
    $ pip install virtualenv virtualenvwrapper

### Make virtualenv
    $ mkvirtualenv --no-site-packages solartools

### Switch to new virtualenv
    $ workon solartools

### Install python dependencies
    $ pip install -r requirements.txt

### Install redis server
    $ brew install redis
    $ ln -sfv /usr/local/opt/redis/*.plist ~/Library/LaunchAgents
    $ launchchtl load ~/Library/LaunchAgents/homebrew.mxcl.redis.plist

### Run solartools
    $ python manage.py runserver


# Using Git in this project (for developers)

Vincent Driessen has written a working model for git branching, which is summarized below.

Follow this guide: http://nvie.com/posts/a-successful-git-branching-model/

## Main branches

The central repo holds two main branches with an infinite lifetime:
* master
* develop

Master can be considered the same as a release and should always be tagged with a version number.

Develop is where all the development originates from and goes to. Develop is then merged into master, when it is ready.

## Feature branches 

May branch off from:
* develop 

Must merge back into:
* develop 

Branch naming convention:
* anything except master, develop, release-*, or hotfix-* 

Feature branches exist in developer repos only, not in origin.

## Creating a feature branch

When starting work on a new feature, branch off from the develop branch.

    $ git checkout -b myfeature develop
    Switched to a new branch "myfeature"

## Incorporating a finished feature on develop

Finished features may be merged into the develop branch definitely add them to the upcoming release:

    $ git checkout develop
    Switched to branch 'develop'
    $ git merge --no-ff myfeature
    Updating ea1b82a..05e9557
    (Summary of changes)
    $ git branch -d myfeature
    Deleted branch myfeature (was 05e9557).
    $ git push origin develop

## Release branches

May branch off from:
* develop

Must merge back into:
* develop and master

Branch naming convention:
* release-* 

## Creating a release branch

    $ git checkout -b release-1.2 develop
    Switched to a new branch "release-1.2"
    $ ./bump-version.sh 1.2
    Files modified successfully, version bumped to 1.2.
    $ git commit -a -m "Bumped version number to 1.2"
    [release-1.2 74d9424] Bumped version number to 1.2
    1 files changed, 1 insertions(+), 1 deletions(-)

bump-version.sh is a fictional shell script that changes some files in the working copy to reflect the new version.

## Finishing a release branch

First, the release branch is merged into master (since every commit on master is a new release by definition). Next, that commit on master must be tagged for easy future reference to this historical version. Finally, the changes made on the release branch need to be merged back into develop, so that future releases also contain these bug fixes.

    $ git checkout master
    Switched to branch 'master'
    $ git merge --no-ff release-1.2
    Merge made by recursive.
    (Summary of changes)
    $ git tag -a 1.2

The release is now done, and tagged for future reference. 

To keep the changes made in the release branch, we need to merge those back into develop, though. 

    $ git checkout develop
    Switched to branch 'develop'
    $ git merge --no-ff release-1.2
    Merge made by recursive.
    (Summary of changes)

Now we are really done and the release branch may be removed, since we don’t need it anymore:

    $ git branch -d release-1.2
    Deleted branch release-1.2 (was ff452fe).

## Hotfix branches

May branch off from:
* master

Must merge back into:
* develop and master

Branch naming convention:
* hotfix-* 

## Creating a hotfix branch

Hotfix branches are created from the master branch. 

    $ git checkout -b hotfix-1.2.1 master
    Switched to a new branch "hotfix-1.2.1"
    $ ./bump-version.sh 1.2.1
    Files modified successfully, version bumped to 1.2.1.
    $ git commit -a -m "Bumped version number to 1.2.1"
    [hotfix-1.2.1 41e61bb] Bumped version number to 1.2.1
    1 files changed, 1 insertions(+), 1 deletions(-)

Then, fix the bug and commit the fix in one or more separate commits.

    $ git commit -m "Fixed severe production problem"
    [hotfix-1.2.1 abbe5d6] Fixed severe production problem
    5 files changed, 32 insertions(+), 17 deletions(-)

Update master and tag the release.

    $ git checkout master
    Switched to branch 'master'
    $ git merge --no-ff hotfix-1.2.1
    Merge made by recursive.
    (Summary of changes)
    $ git tag -a 1.2.1

Include the bugfix in develop

    $ git checkout develop
    Switched to branch 'develop'
    $ git merge --no-ff hotfix-1.2.1
    Merge made by recursive.
    (Summary of changes)

Finally, remove the temporary branch:

    $ git branch -d hotfix-1.2.1
    Deleted branch hotfix-1.2.1 (was abbe5d6).

# Version numbering (for developers)

Try to follow semantic numbering scheme from http://semver.org/

Releases (ie. all commits) on the master are tagged with vX.Y.Z.

Given a version number MAJOR.MINOR.PATCH, increment the:
* MAJOR version when you make incompatible API changes,
* MINOR version when you add functionality in a backwards-compatible manner, and
* PATCH version when you make backwards-compatible bug fixes.

