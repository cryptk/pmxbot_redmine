import setuptools

setup_params = dict(
    name="pmxbot-redmine",
    version = "0.6.4",
    packages=setuptools.find_packages(),
    entry_points=dict(
        pmxbot_handlers = [
            'redmine = pmxbot_redmine',
        ]
    ),
    description="Integrate redmine with pmxbot",
    license = 'MIT',
    author="Chris Jowett",
    author_email="cryptk@gmail.com",
    maintainer = 'Chris Jowett',
    maintainer_email = 'cryptk@gmail.com',
    url = 'https://www.cryptkcoding.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: Chat',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
    ],
)

if __name__ == '__main__':
    setuptools.setup(**setup_params)
