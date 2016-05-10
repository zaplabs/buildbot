from buildbot.plugins import steps, util

def build(cfg, buildname):
	bf = util.BuildFactory()
	bf.addStep(
		steps.Git(
			repourl=cfg['url'],
			branch=cfg['branch'],
			mode='full',
			logEnviron=False
		)
	)
	if 'gitversion' in cfg:
		bf.addStep(cfg['gitversion'])
	bf.addStep(
		steps.ShellCommand(
			name="fetch support",
			command=["git", "clone", "--depth=1", "--branch=mame", "https://github.com/zaplabs/buildsupport.git", ".buildsupport"],
			description="download latest build support tool",
			haltOnFailure=True
		)
	)
	bf.addStep(
		steps.Compile(
			command=['bash', '-c', '.buildsupport/build.sh'],
			haltOnFailure=True
		)
	)
	bf.addStep(
		steps.ShellCommand(
			name="package",
			command=['bash', '-c', '.buildsupport/release.sh'],
			haltOnFailure=True, flunkOnFailure=True
		)
	)
	bf.addStep(
		steps.MultipleFileUpload(
			slavesrcs=[
				util.Interpolate("mame-mingw-gcc-x64-%(prop:gitversion)s.md5"),
				util.Interpolate("mame-mingw-gcc-x64-%(prop:gitversion)s.exe"),
			],
			masterdest="~/sites/com.zaplabs/build/public/project/mame/archive",
			url="/project/mame",
			haltOnFailure=False, flunkOnFailure=False, mode=0644
		)
	)
	return bf