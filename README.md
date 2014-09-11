pmxbot_redmine
==============

pmxbot plugin for searching redmine issues

Setup
=====
1. Get PmxBot running in your channel (https://bitbucket.org/yougov/pmxbot/overview)
2. Clone this repository
3. Within the clone `python setup.py bdist_egg`
4. This will create an egg file within /path/to/clone/dist/, install it with `sudo easy_install /path/to/clone/dist/pmxbot_redmine-version-pyversion.egg`

Configuration
=============

```yaml
redmine_apikey: "your_redmine_API_key"
redmine_url: "http://yourredmineurl.com/"
redmine_chan_proj_mapping:
  "#channel1":
    - "someproject"
  "#channel2":
    - "someproject"
    - "someotherproject"
```

**redmine_apikey**: should be set to a valid API key in redmine that has access to every redmine project that the bot will read from

**redmine_url**: should be set to the URL that your redmine install is located at

**redmine_chan_proj_mapping**: determines what IRC channels are allowed to get data from what redmine projects. The intent here is that you can allow some projects to be queried from one channel while only allowing other projects to be queried from other channels. The channels should be input exactly as they would be in IRC (including the # if it is part of the channel name). The projects that are listed are the project identifier (not the project name)

Usage
=====
**Redmine ticket links**: If you mention a redmine issue number in the format #1234, then JebBot will attempt to look that ticket up in redmine and provide a link to it.
```
<someuser> you can query the link to a bug by saying #1234 anywhere within a statement
<PmxBot> someuser: http://yourredmineurl.com/issues/1234
```

**Redmine ticket details**: If you would like a short synopsis of a redmine issue, you can use the !bug command to look it up
```
<someuser> !bug 1234
<PmxBot> someuser: 1234 is http://yourredmineurl.com/issues/1234 "Some Project - Broken: The widget in the foo interface cannot be clicked" It's status is New and is assigned to SomeDeveloper
```
