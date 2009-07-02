from distutils.core import setup


def main():
    setup(name = "pyregion",
          version = "0.1a",
          description = "python parser for ds9 region files",
          author = "Jae-Joon Lee",
          author_email = "lee.j.joon@gmail.com",
          url="http://leejjoon.github.com/pyregion/",
          #maintainer_email = "lee.j.joon@gmail.com",
          license = "MID",
          platforms = ["Linux","Mac OS X"], # "Solaris"?
          packages = ['pyregion'],
          package_dir={'pyregion':'lib'},
          #test_suite = 'nose.collector',
          )


if __name__ == "__main__":
    main()
