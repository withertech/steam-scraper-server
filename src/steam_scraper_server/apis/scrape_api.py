# coding: utf-8
from __future__ import annotations

import os
import subprocess
from typing import Dict, List  # noqa: F401
from urllib.parse import quote

import jwt
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
    status, HTTPException,
)
from jwt import InvalidSignatureError
from tortoise.exceptions import DoesNotExist

from steam_scraper_server import global_vars
from steam_scraper_server.apis import security_api
from steam_scraper_server.db.user import User
from steam_scraper_server.db.rom import Rom, Media
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
        key: str = Depends(security_api.oauth2)
) -> ImagesResult | ErrorResult:
    try:
        payload = jwt.decode(key, global_vars.AUTH_SECRET, algorithms=["HS256"])
        user_ = await User.get(username=payload.get("username"))
    except (DoesNotExist, InvalidSignatureError):
        try:
            payload = jwt.decode(jwt.decode(key, global_vars.SCRAPE_SECRET, algorithms=["HS256"]).get("token"),
                                 global_vars.AUTH_SECRET, algorithms=["HS256"])
            user_ = await User.get(username=payload.get("username"))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Credentials"
            )
    md5 = md5.upper()
    try:
        if not (await Rom.exists(md5=md5)):
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
                print(folder)
                rom_path = os.path.join(folder, filename)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                with open(rom_path, 'w'):
                    pass
                if runcmd([
                    'Steamscraper',
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
                    rom_path
                ]).decode().find('Successfully processed games: 1') != -1:
                    rom = await Rom.create(md5=md5, system=platform)
                    await rom.save()
                    break
                os.remove(rom_path)
        elif await Media.exists(md5=md5):
            rom = await Rom.get(md5=md5)
            media = await Media.get(md5=md5)
            return ImagesResult(name=filename, system=rom.system, images=ImagesResultImages(
                head=media.head,
                tall=media.tall,
                hero=media.hero,
                logo=media.logo,
                icon=media.icon
            ))
        else:
            rom = await Rom.get(md5=md5)
            folder = os.path.join('/opt/scraper/roms', rom.system)
            rom_path = os.path.join(folder, filename)
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(rom_path, 'w'):
                pass
            runcmd([
                'Steamscraper',
                '-p',
                rom.system,
                '-s',
                'screenscraper',
                '--lang',
                'en',
                '--region',
                'us',
                '--query',
                'md5=' + md5,
                rom_path
            ])
            os.remove(rom_path)
        rom = await Rom.get(md5=md5)
        folder = os.path.join('/opt/scraper/roms', rom.system)
        rom_path = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(rom_path, 'w'):
            pass
        runcmd([
            'Steamscraper',
            '-p',
            rom.system,
            '--lang',
            'en',
            '--region',
            'us',
            '--query',
            'md5=' + md5,
            rom_path
        ])
        os.remove(rom_path)
        media = await Media.create(
            md5=md5,
            head=F"https://repo.withertech.com/scraper/images/"
                 F"{rom.system}/steamgrids/{quote(os.path.splitext(filename)[0] + '.png')}",
            tall=F"https://repo.withertech.com/scraper/images/"
                 F"{rom.system}/covers/{quote(os.path.splitext(filename)[0] + '.png')}",
            hero=F"https://repo.withertech.com/scraper/images/"
                 F"{rom.system}/heroes/{quote(os.path.splitext(filename)[0] + '.png')}",
            logo=F"https://repo.withertech.com/scraper/images/"
                 F"{rom.system}/logos/{quote(os.path.splitext(filename)[0] + '.png')}",
            icon=F"https://repo.withertech.com/scraper/images/"
                 F"{rom.system}/icons/{quote(os.path.splitext(filename)[0] + '.png')}"
        )
        await media.save()
        res = ImagesResult(name=filename, system=rom.system, images=ImagesResultImages(
            head=media.head,
            tall=media.tall,
            hero=media.hero,
            logo=media.logo,
            icon=media.icon
        ))

        return res
    except HTTPException as e:
        print(e)
        return ErrorResult(code=e.status_code, message=e.detail)
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
