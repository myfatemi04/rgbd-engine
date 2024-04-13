from setuptools import setup, find_packages

setup(
    name='rgbdengine',
    version='0.0.0.dev1',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'numpy',
        'pyk4a',
        # 'apriltag'
    ],
    author='Michael Fatemi',
    author_email='gsk6me@virginia.edu',
    description='RGBD Camera API for working with Azure Kinect cameras and AprilTags',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/myfatemi04/rgbd-engine',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
