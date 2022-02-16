<# 
 param (  
    [Parameter(Mandatory=$true)][string]$REPO_URL,
    [Parameter(Mandatory=$true)][string]$BRANCH_NAME,
    [Parameter(Mandatory=$true)][string]$GIT_PULL_DIR,
    [Parameter(Mandatory=$true)][string]$SOLUTION_FILE,
    [Parameter(Mandatory=$true)][string]$deploy_dir)
 )

#>
# Think to manage these variables with jenkins or without it
###################################################################
$REPO_URL="$env:REPO_URL"
$REPO_PASSWORD="$env:REPO_PASSWORD"
$BRANCH_NAME="$env:BRANCH_NAME"
$GIT_PULL_DIR="$env:GIT_PULL_DIR"
$SOLUTION_FILE="$env:SOLUTION_FILE"
$deploy_dir="$env:deploy_dir"
###################################################################
## Creating required variables
############ $shared_folder="\\IN-568\builds" #################
#$shared_folder="\\IN-4KB\builds"

$timestamp=Get-Date -Format u
$timestamp=$timestamp.Substring(0,$timestamp.Length-1).Replace(" ","_").Replace(":","_")
Write-host "Current_time_stamp $timestamp"

#$GIT_PULL_DIR="C:\temp_dir"
# For Jenkins
$GIT_PULL_DIR="$ENV:WORKSPACE"
$project_name=$REPO_URL.split("/")[-1].Replace(".git","")
$build_dir="$GIT_PULL_DIR\$project_name\Pipeline"


$SOLUTION_FILE="$GIT_PULL_DIR\clean\Pipeline\Pipeline.sln"

$char_position=$REPO_URL.IndexOf("@")
$repo_url_with_creds=$REPO_URL.Insert($char_position,":$REPO_PASSWORD")
###################################################################

# This part gives the msbuild path

#Find .Net Framework MSBuid path on the machine
Function Find-MsBuild([int] $MaxVersion = 2017)
{
    $agentPath = "$Env:programfiles (x86)\Microsoft Visual Studio\2017\BuildTools\MSBuild\15.0\Bin\msbuild.exe"
    $devPath = "$Env:programfiles (x86)\Microsoft Visual Studio\2017\Enterprise\MSBuild\15.0\Bin\msbuild.exe"
    $proPath = "$Env:programfiles (x86)\Microsoft Visual Studio\2017\Professional\MSBuild\15.0\Bin\msbuild.exe"
    $communityPath = "$Env:programfiles (x86)\Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\msbuild.exe"
    $fallback2015Path = "${Env:ProgramFiles(x86)}\MSBuild\14.0\Bin\MSBuild.exe"
    $fallback2013Path = "${Env:ProgramFiles(x86)}\MSBuild\12.0\Bin\MSBuild.exe"
    $fallbackPath = "C:\Windows\Microsoft.NET\Framework\v4.0.30319"
		
    If ((2017 -le $MaxVersion) -And (Test-Path $agentPath)) { return $agentPath } 
    If ((2017 -le $MaxVersion) -And (Test-Path $devPath)) { return $devPath } 
    If ((2017 -le $MaxVersion) -And (Test-Path $proPath)) { return $proPath } 
    If ((2017 -le $MaxVersion) -And (Test-Path $communityPath)) { return $communityPath } 
    If ((2015 -le $MaxVersion) -And (Test-Path $fallback2015Path)) { return $fallback2015Path } 
    If ((2013 -le $MaxVersion) -And (Test-Path $fallback2013Path)) { return $fallback2013Path } 
    If (Test-Path $fallbackPath) { return $fallbackPath } 
        
    throw "Yikes - Unable to find msbuild"
    Write-Host "`n"
}


function check_and_fetch_git {
param([string]$GIT_PULL_DIR,[string]$BRANCH_NAME,[string]$REPO_URL)

$bool_status=Test-Path -Path $GIT_PULL_DIR
Write-Host "Check Git directory and create if not exists - Result: $bool_status"

if(!(Test-Path -Path $GIT_PULL_DIR ))
{   
    Write-host "Repository Directory: $GIT_PULL_DIR does not exist, creating it"
    New-Item -ItemType directory -Path $GIT_PULL_DIR
}
else
{
Write-host "Repository Directory: $GIT_PULL_DIR already exists, going ahead..." 
}

$project_name=$REPO_URL.split("/")[-1].Replace(".git","")

$bool_status=Test-Path -Path "$GIT_PULL_DIR\$project_name"
Write-Host "Check if the directory contains .git directory of the repository - Result: $bool_status"
$git="C:\Program Files\Git\bin\git.exe"
if(!(Test-Path -Path "$GIT_PULL_DIR\$project_name\.git" ))
{
    Write-Host ".git Absent: Clone of the repository is not Present"
    cd $GIT_PULL_DIR

    Write-host "Starting git clone in directory $pwd"
  
    & $git clone $repo_url_with_creds
    & $git checkout $BRANCH_NAME

}
else
{
    Write-host ".git Present: Repository already cloned in $GIT_PULL_DIR\$project_name, Fteching latest commits" 
    cd "$GIT_PULL_DIR\$project_name"
    & $git checkout $BRANCH_NAME
    & $git fetch $repo_url_with_creds $BRANCH_NAME
}
        

Write-Host "`n"
}

function nuget_and_packages_download {
param([string]$GIT_PULL_DIR,[string]$SOLUTION_FILE)

	$nuget_url = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"
	$output = "nuget.exe"
	$start_time = Get-Date
	$nuget_exe=$GIT_PULL_DIR+"\"+$output

	cd $GIT_PULL_DIR
	Write-Host "Starting with downloading nuget.exe"
	Invoke-WebRequest -Uri $nuget_url -OutFile $output
	Write-Host "nuget.exe : Download Complete"
	write-host "Time taken: $((Get-Date).Subtract($start_time).Seconds) second(s)"

Try
{
    Write-Host "Starting with downloading nuget.exe"
    & $nuget_exe restore $SOLUTION_FILE
    ##& 'C:\Program Files\Nuget\nuget.exe' restore $SOLUTION_FILE
}
Catch
{
    $ErrorMessage = $_.Exception.Message
    Write-Host "This is Error $ErrorMessage"
    Break
}

Write-Host "`n"

}

Write-Host "MSBUILD:"


Write-Host "Build Directory $build_dir"
$msbuild_exe=(Find-MsBuild  -MaxVersion 2015)
Write-Host "Path of the MSBUILD on this Computer $msbuild_exe"


Write-Host "Git Check:"
check_and_fetch_git -GIT_PULL_DIR $GIT_PULL_DIR -BRANCH_NAME $BRANCH_NAME -REPO_URL $REPO_URL


Write-Host "Nuget and Packages Download:"
nuget_and_packages_download -GIT_PULL_DIR $GIT_PULL_DIR -SOLUTION_FILE $SOLUTION_FILE


Write-Host "Compilation:"
& $msbuild_exe $SOLUTION_FILE  "/t:Clean,Build"


## Uploading the created build on aws for test
cd $build_dir/../


#aws sts assume-role  --role-arn "arn:aws:iam::<aws-account-id>:role/<role_name>" --duration-seconds 3600 --role-session-name 'file1'

aws s3 cp ./ s3://mcr-devops/releases/project_name/$timestamp/ --recursive --acl bucket-owner-read