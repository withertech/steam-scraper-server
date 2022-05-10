# coding: utf-8
from __future__ import annotations

import os
import subprocess
from typing import Dict, List  # noqa: F401
from urllib.parse import quote
import fastapi
import plyvel
import requests
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
)
from pydantic.networks import HttpUrl

from steam_scraper_server.models.error_result import ErrorResult
from steam_scraper_server.models.extra_models import TokenModel  # noqa: F401
from steam_scraper_server.models.images_result import ImagesResult
from steam_scraper_server.models.images_result_images import ImagesResultImages

router = APIRouter()


@router.get(
    "/scrape",
    responses={
        200: {"model": ImagesResult, "description": "Urls to the images for the rom"},
        0: {"model": ErrorResult, "description": "unexpected error"},
    },
    tags=["scrape"],
    summary="Scrape a rom",
    description="Scrapes a rom for steam rom manager from screenscraper.fr using name of file and md5 sum"
)
async def scrape(
        filename: str = Query(None, description="name of the rom"),
        md5: str = Query(None, description="md5 of the rom"),
) -> ImagesResult | ErrorResult:
    try:
        if not os.path.exists('/opt/scraper/platformdb/'):
            os.makedirs('/opt/scraper/platformdb/')
        db = plyvel.DB('/opt/scraper/platformdb/', create_if_missing=True)

        if db.get(str.encode(md5)) is None:
            for platform in ['3do', '3ds', 'amiga',
                             'amigacd32', 'amstradcpc', 'apple2', 'arcade',
                             'arcadia', 'astrocde', 'atari800', 'atari2600',
                             'atari5200', 'atari7800', 'atarijaguar',
                             'atarijaguarcd', 'atarilynx', 'atarist',
                             'atomiswave', 'c16', 'c64', 'c128', 'channelf',
                             'coco', 'coleco', 'daphne', 'dragon32',
                             'dreamcast', 'easyrpg', 'fba', 'fds',
                             'gameandwatch', 'gamegear', 'gb', 'gba', 'gbc',
                             'gc', 'genesis', 'intellivision', 'mame-advmame',
                             'mame-libretro', 'mame-mame4all', 'mastersystem',
                             'megacd', 'megadrive', 'moto', 'msx', 'msx2',
                             'n64', 'naomi', 'nds', 'neogeo', 'neogeocd',
                             'nes', 'ngp', 'ngpc', 'openbor', 'oric', 'pc',
                             'pc88', 'pc98', 'pcfx', 'pcengine', 'pcenginecd',
                             'pokemini', 'ports', 'ps2', 'psp', 'psx',
                             'saturn', 'scummvm', 'sega32x', 'segacd',
                             'sg-1000', 'snes', 'steam', 'switch', 'ti99',
                             'trs-80', 'vectrex', 'vic20', 'videopac',
                             'virtualboy', 'wii', 'wiiu', 'wonderswan',
                             'wonderswancolor', 'x68000', 'x1', 'zmachine',
                             'zx81', 'zxspectrum']:
                folder = os.path.join('/opt/scraper/roms', platform)
                rom = os.path.join(folder, filename)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                with open(rom, 'w'):
                    pass
                if runcmd([
                    'SteamScraper',
                    '-p',
                    platform,
                    '-s',
                    'screenscraper',
                    '--lang',
                    'en',
                    '--region',
                    'us',
                    '--query',
                    'md5=' + md5,
                    rom
                ]).decode().find('Successfully processed games: 1') != -1:
                    db.put(str.encode(md5), str.encode(platform))
                    break
                os.remove(rom)
        else:
            platform = db.get(str.encode(md5)).decode()
            folder = os.path.join('/opt/scraper/roms', platform)
            rom = os.path.join(folder, filename)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(rom, 'w'):
                pass
            runcmd([
                'SteamScraper',
                '-p',
                platform,
                '-s',
                'screenscraper',
                '--lang',
                'en',
                '--region',
                'us',
                '--query',
                'md5=' + md5,
                rom
            ])
            os.remove(rom)
        platform = db.get(str.encode(md5)).decode()
        folder = os.path.join('/opt/scraper/roms', platform)
        rom = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(rom, 'w'):
            pass
        runcmd([
            'SteamScraper',
            '-p',
            platform,
            '--lang',
            'en',
            '--region',
            'us',
            '--query',
            'md5=' + md5,
            rom
        ])
        os.remove(rom)
        print()
        res = ImagesResult(name=filename, system=db.get(str.encode(md5)).decode(), images=ImagesResultImages(
            head=F"https://repo.withertech.com/scraper/images/"
                 F"{platform}/steamgrids/{quote(os.path.splitext(filename)[0] + '.png')}",
            tall=F"https://repo.withertech.com/scraper/images/"
                 F"{platform}/covers/{quote(os.path.splitext(filename)[0] + '.png')}",
            hero=F"https://repo.withertech.com/scraper/images/"
                 F"{platform}/heroes/{quote(os.path.splitext(filename)[0] + '.png')}",
            logo=F"https://repo.withertech.com/scraper/images/"
                 F"{platform}/logos/{quote(os.path.splitext(filename)[0] + '.png')}",
            icon=F"https://repo.withertech.com/scraper/images/"
                 F"{platform}/icons/{quote(os.path.splitext(filename)[0] + '.png')}"
        ))

        return res
    except RunCmdException as e:
        print(e)
        return ErrorResult(code=e.returncode, message=e.output)
    except OSError as e:
        print(e)
        return ErrorResult(code=e.errno, message=e.strerror)


class RunCmdException(Exception):
    def __init__(self, msg, returncode, output):
        super(RunCmdException, self).__init__(msg)
        self.output = output
        self.returncode = returncode


def runcmd(cmd, stdin=None, debug=True):
    """
    Run command specified by list `cmd` in a blocking fashion. If stdin is provided, feed it
    to the process. Raise `RunCmdException` if the return code of the process is not 0. Return
    a string with the combined stdout and stderr of the process.
    """

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    if stdin is not None:
        proc.stdin.write(stdin)
    proc.stdin.close()
    proc.wait()
    o = proc.stdout.read()

    if proc.returncode > 0:
        raise RunCmdException("Command '%s' failed" % " ".join(cmd), proc.returncode, o)
    return o
