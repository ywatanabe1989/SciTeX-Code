#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 08:02:27 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_01-url.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates ScholarURLFinder capabilities for PDF discovery
- Shows URL resolution through multiple methods (DOI, OpenURL, Zotero translators)
- Validates authenticated browser context for URL finding
- Displays comprehensive URL finding results

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- DOI for URL resolution
- Authenticated browser context

Output:
- Console output with discovered URLs and their sources
- PDF URLs from multiple discovery methods
"""

"""Imports"""
import argparse
import asyncio
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_url_finding(
    doi: str = None, use_cache: bool = False
) -> dict:
    """Demonstrate URL finding capabilities.

    Parameters
    ----------
    doi : str, optional
        DOI to find URLs for
    use_cache : bool, default=False
        Whether to use cached results

    Returns
    -------
    dict
        URL finding results
    """
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarURLFinder,
    )

    search_doi = doi or "10.1016/j.smrv.2020.101353"

    print("🌐 Initializing authenticated browser context...")
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="interactive",
        chrome_profile_name="system",
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    print(f"🔍 Creating URL finder (cache: {use_cache})...")
    url_finder = ScholarURLFinder(context, use_cache=use_cache)

    print(f"🔗 Finding URLs for DOI: {search_doi}")
    urls = await url_finder.find_urls(doi=search_doi)

    print("📊 URL Finding Results:")
    print("=" * 50)
    pprint(urls)

    return urls


async def main_async(args) -> dict:
    """Main async function to demonstrate URL finding.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    dict
        URL finding results
    """
    print("🔗 Scholar URL Finder Demonstration")
    print("=" * 40)

    results = await demonstrate_url_finding(
        doi=args.doi, use_cache=not args.no_cache
    )

    print("✅ URL finding demonstration completed")
    return results


def main(args) -> int:
    """Main function wrapper for asyncio execution.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit status code (0 for success, 1 for failure)
    """
    try:
        asyncio.run(main_async(args))
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Scholar URL finding capabilities"
    )
    parser.add_argument(
        "--doi",
        "-d",
        type=str,
        # default="10.1016/j.smrv.2020.101353",
        default="10.1016/j.neubiorev.2020.07.005",
        help="DOI to find URLs for (default: %(default)s)",
    )
    # https://doi.org/10.1016/j.neubiorev.2020.07.005
    # Should be pdf_url: https://pdf.sciencedirectassets.com/271127/1-s2.0-S0149763420X00108/1-s2.0-S0149763420304668/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEK3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIBkY4pDqK%2FdNCtcxAcHCRHS8fOsOEzK1aZxwOLRzLD%2BFAiBzRTiyykWiS22B%2BZ7jDlINENJHytfJueaVltMC1EYPvSq7BQj1%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAUaDDA1OTAwMzU0Njg2NSIMMTkY0jOt%2FbdL%2FIohKo8FRRm5uSk0vZSU0m7ZeZMR96khTGQxhRl%2FplpzNlDpw6NEdhHYiTwSnGi84t9aOMYNmz8TB43vjnfJ3YmxApWhyNK39HiVTtuzv2ujQT8bwNCj8%2BMHmblRDHnQcn%2F5PnGBjmPUkzBT3inl3zYKGT3VcKBdHckrInLZD7xeEFmjUa42nIExTwoJ7ngig926XxFHddFp4G2tTxKpp9jp0XCP1DKpemdTWyveqC4m1TZMZ1qjZPkQF%2FRyxlCofdHmVUzFGSsWUl6iHgwWoqMISm0y5SRHwleQUHrmEx8I3cak9zeim3NCHlwDGPz8OTmzS7keZCPVqHMqDvkWYDsT3%2BHsbBWRmju8Llmid7R26LE9Wy%2BtlL%2BmrB1ON46Rv01dkeSdeslPjdBJ8q5niHwFnpsQVmpnxcWmCy03xNrjEirluu4jc%2BKAWabiVtjREB3s0TAGN9q0cykW1QA9Gp9y2FEoK9HIE3OL6JgUvLq30ql%2Bwy49cv6Q0xA%2FfXohHbpnX2Jh75%2BWNaK3dELUxQFXBWfSJUUxjrXFL%2F5Ve0598EJHDZKiLKwkIldVHYgB9LG8b0ja7bP5znnYND0MHuZRNLQUbLRmxp9q9aD6vQovNjLyka9nD39EgDXHD6m2%2Fh4GmacXPoZ%2F%2BknaKJITmYL00abd2JY5mhC1xiosLLd29HwwpeJ3fAbP4cP7d4IqV4he%2BrxCXOcLhXrTgFBxIiX303rFfY88QVl7l6sHRn6hFJMPQi9dpAw9CtqMbhne5YTXWp59wygh4sZoRJ1Ark409okqji1kSTzC7ncb%2BD%2BJh7n7XmoAD8gqlnW8pT1vvlfLIfOGObqbGzokaUQF5fE%2FPKiifNYWJQ0FEuJ6rACcJptamDC%2B%2Bp3FBjqyAVvoerBridFKX0Oeukb99Q9%2BOQPNyqUp2a6cIqsCe%2BUmxYi7BpTiCymfPpNfXLv%2BF3NPOU85gD2gmFfSxiKNM1JXMcnMRlz8uhRslLa7NeXLZIvzXeaaV%2BaB%2Bm%2F1t%2FR8l5xJCX%2F7ur%2FUd2nK6RlgrlAbcjLAx%2BkucEB2OdrbYe9rf8w6ijem6z%2FNSD9znKmRTk21Oonr1oOiGDNAdsCQagM35eTjn2O%2BXruhVZhUTDU9fUo%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250821T212938Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTY6S63PFP3%2F20250821%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=481f877cab3248bb45e5c4762a4e17979e4ad4ee36522484ae8df27ffb2dc634&hash=4d8b13ad734d0750fce9eb3919e2748b4e47eb9d12074bd864bb161c0cbae374&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0149763420304668&tid=spdf-77a1c9c6-3c01-4e80-ae0c-51f3885f03a7&sid=431f6c301fd0d54c2e2b42d653e6f345dca4gxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&rh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=1b105955550b54025751&rr=972d3a213932e6ab&cc=au

    # https://doi.org/10.1016/j.smrv.2020.101353
    # Should be pdf_url: https://pdf.sciencedirectassets.com/272527/1-s2.0-S1087079220X00050/1-s2.0-S1087079220300964/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEK3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQDAYGxygR%2BeExC3vSObVuIQSs1IsOdfHZ%2BjU4qaDRVd5AIhAJhLCSXez5lcd1oud4xrUVT4psimNJQPjBBGrQhdtLOYKrwFCPb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQBRoMMDU5MDAzNTQ2ODY1IgzHVtrG9v4tn7hHDdkqkAX93WFxOtlkoU0H5AlM%2BKKw5oWegeEslYziJqUoBuFzAlZnTtnbSCnqJva4mZRI%2B1nawORi6XMfcTSM8jGV9UnyyBxU0Yf8qHvhQ6I6rYfTsfh5hzz%2FM0TtaVrelx5kEpwhR3e5GMCPdG2MdiYixX4JvR0TBuZujfsin9afvmnszZDw2%2F0kl0USOlPChHzeTWu7JtS%2BbJZbvQJdUCtUbNmu3HHOPY9fOm%2Fzo2Zvb7FEVVWETyTZ%2B9PVb2biKqwUNrkN9x6Cu2sjH6Zscu%2FSx%2BwTJIkpiQnGGUVCd8Xccml1MCEG0Gz3V9byGWn58eeT0aWdyVcxH013hhiBxqQILYgZlKtqfMIAAThUC8N%2FA9T64OVRs5m46KkOAfkVPRbS%2Ba5PdG3EZDk5q%2Bb1z8plHZYLrakt26J6c3xpYPOeIXkusDIkA2iJLZFaKB4sv8UWeeXrFOa5EcpgrtJPT%2BY8%2FPa%2Fb1ZhIMJ9w%2ByIdm%2FMgs9RGydMNc6tEaW2Hk%2FZ7uix2wev2tHu0j1aRdB2KulIZLHxAklzRLnR35rqhBNC4I3nVIOZrZRBdqo1MTy%2BV7x81dTmkq0zSf38GVPYFnfPeSav4j89plOZs2MvOlN6zlc0ONqXDoUHE53musFeZu95MHzzjQr8%2FNKtnd%2F4G2ac5TGIQmDe1dR9ZncsQ2gkEfg4juj5HXCcg1JlhtgbMAs5oGcw1UJyeKNEUhxLLAjHw0p%2FDirTn3cMfyWeXDY%2BpKKA4eK5x2YEcW3jPd7sG%2BmofQyxBW0oH7RLN%2Bz0TWRBl8sblUJ6Wt4L%2FGWMZ7SgUbF%2FTueovJuCZDI1k0UieqIQy0S%2FwxR%2BrpCd6MOjIdJjpXrrlNITKf4Qrqo7kyF0E7q9%2BDDBjp7FBjqwAY4hjyoY93%2Bf8B3RmBNusvVm01%2BQxY8V390Z3r7gdxPBFx2NQLlp0ebg%2BFoal1OjhAIO%2Blpna6TfoIx12WCfjd8rWZyveuAle5FvlODm6PGZv%2FR1A2ol5Xdb5E8dfHPChiuSLOz8juFaZihFH6FwZtn76fXGUY9oadfNNyQ3fHAIZ%2BvURS1P1ik3FQuyFsyt6t9tQXw6EF6wxaGnsM5c2JlM1OnGMYdJ9OW23qLF8PmP&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250821T211232Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYTV7MA7GJ%2F20250821%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=3c44983841589d3435cd369f52ae39ccd4746d9127e9c32775b190ab8af02522&hash=f2e5afe665a2e80556e34c583e222d8f5dfa471a216f216d3989d8d02f568333&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S1087079220300964&tid=spdf-6275680f-19be-40f8-9526-18678004f69e&sid=39528439443a5141ab78651427de0c469842gxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&rh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=1b1a575155035451530c&rr=972d210c3ef3cfbb&cc=au

    # https://doi.org/10.1016/j.neuroimage.2021.118403
    # Should be pdf_url: https://pdf.sciencedirectassets.com/272508/1-s2.0-S1053811921X00134/1-s2.0-S1053811921006789/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKz%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIDgVEORvSOxcbh3iWnEuhyll9D144KH5SFNzsmCpWCu7AiEAnpNSunfyNR8CR8E1rmMNh%2BIoKfEFC0Mvmjh4YCUcrXUquwUI9f%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAFGgwwNTkwMDM1NDY4NjUiDByesTIfH9WlY7ToqiqPBdkSFFGBPN9qGjeJo5Pj1gukkSAbKzeeOgV5hcJMnBGBM%2Bucnn6HiwqeyFJF%2BB5%2BePPTyiSt7vPV0xT63NAX0LJrt5lwL9mkNwENO8X0aGT22rMfdi2SVRvb905Hop58NVMYIagELsydWRobLaSyLkX24yV8ASpb3m68iCSNyijrkz7cE8%2BcoyuYbrVee1PrQ6gkE52Z6CEhxZmtlIiCdgMmNptsi0IEeGjj%2FKdRzEId3m%2BiT6dzQbt%2F0UfkrGOaCc8LQ8A9lMdfkgGpOD8Ngp7WCPCovNFUMmx0w41tVEg3ihVZ%2BriC%2BBa2iiU31u5rZqMenvi8PdC7revOMkrKZetcV5wg9Cm3BHv926WG6MqVylrnUtZgUL6QY9xMsjmAu8IaUzsewE1fEUyxnC0%2Fbcj78gYnqA3FsDOiWWOl2712eJhVd30hml0J6iDEmQDF%2FWQYaPLx8rAH%2BXNRi3aLmc7Xd%2FJSVkknYM0SCaO70yHAaI7VEorkr5ktUDwHnmiYifsKQAVCk6MWxQquKCdv4GeXw4aHGDGgTrb6rSAG3W97KLQa%2BJVWo4oq3AQMtD1xPMJ6hP3%2FGyDP%2B7PRZTnKny792H%2FftdIMnEjQb8yq36oHxlStYao35%2BkyFlPk1kXXFk8W36itDBOFABfpEyMfo%2FBzADfKzQT526BsGYDPL7hgAVHhQZOMsFEjuUyD2ImNcDQ9%2BwxLZ0rts3lFig%2FqpyGDnJAivtOFICVuAwuSWBJmObqUUAxmEPNIgteG%2FcI%2FN8nAzvMfmngx6wM8zDdLWhySUJ9wdoaAHHAjOq4To9aSz5ZdljBK1i6tavphtxUtpa%2FWQ7usv0hjKhnq%2BGvzKktk9L1bv9%2Bl8TW4qePE8OAw8%2FadxQY6sQEFpOVXPBDadpNCY1aO4%2B0SOYuG6wryxN5f1exDCh2PGmvwD%2Bd3vOOmwndOlO0aKy0Gm3w6Y7nrgUArhyvRF%2B186veWdQe2am25e6B5SE%2BmilDNpciofEC1cDXrmUkbDI6ausughGqrOLVemT3Djlj8UMPNrmFwGUmmVda6s5UpMfYOWypktbMRPLZzTT4XEVB5q8twRFdI5rBpXv2rzKXgdiqgi92WBU916Bosl6B%2BsDE%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250821T211306Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYVCNXCLKD%2F20250821%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=e1e51576df64cdcd88702687cf2c62611a3dbaf1f4d464ac0264b175d31a14e6&hash=7200eaeb96dd985c096ec6d036c219e2682af78268ac49c7ed45ff69e4c18faa&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S1053811921006789&tid=spdf-8492a1b9-2063-4ec1-ae60-290d92997506&sid=39528439443a5141ab78651427de0c469842gxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&rh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=1b1a5751550354510658&rr=972d21e75862cfbb&cc=au

    # https://doi.org/10.1016/j.neuroimage.2021.118573
    # https://pdf.sciencedirectassets.com/272508/1-s2.0-S1053811921X00171/1-s2.0-S1053811921008466/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEK3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQDdLp%2FBBgY%2B4UTiMQMqBetGOk3%2F9EL%2FZtniO7ETr9qMtQIhAPT9%2FiRKEmuvezojRvVr26nDm9mGmZVbSnYaFHIetAuUKrwFCPb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQBRoMMDU5MDAzNTQ2ODY1IgxTQ6mujZeKetn6PsYqkAU5yLqMqqnpyS3dy4IZTqML0EU0HOXdxDaAf4Ak5WBdCTsZZuu580tkDHdvrotFRblGg9u1mlUmL3Tsoxgh5JFC8YdSYcD6q2WzGeChqxA23t8phgjDUM8pQyReK65z1ra76DJ8unxM1Wo65EMkp05CagUCYEhhE8fxsvAf57OZTYgUC02M0w0o8BJ4OaH9tserWEqBiQe%2BFv0Or6qCoasSC9kCR3QEu6%2Fgmgr5v96yGUI1iEFTYcoXm63OW5gF203S9kAMnLide7XLbRoA9yjEG7oV6tDOLxpAHOQzWRYp7XYPSOlbvndzfQqsbmmq%2Baz9arcE3jFv4hLNRws3wFVznadB4B0VkPIJbnq0F9d2VeVUx4hdxeBcqYzDVEDCoCJ2%2F7PkDiX%2BxUvlfZRco8ZI657HZvs5Ivr5IlbOTaABvaa5%2FnYTkF6PcBgrAe2YD17M2HizKJZIPR%2BCck20r7V2PTdpxauyZDhWMUlABDHO7tjOVh3KmkNvkLnrjozzY9Er3kQJHzwOcZykF5XETI%2FDdmCr1FX2%2FtIzq5fmmNv3fE4dVxA7uPJ6ER6pjEV177o76UffUcPpa7ZR%2BMkidB%2BlApFASkmNYGshrMpDL0TORqilmWlKG1jyhH5JN4Cwoqu464uV1DmqjQbU%2B5YLirY5URtFdPRJV9lKUc98MCN7g2bSrh91tqz9S5Su32EVMGwbJx0FyXix%2BUFFP%2FCVsJvkKVZD2kmVNMelqKKU1uwZhfXhZMsK2fe0ZQLedQMJenUQJH4Xrq2gFEKXjX%2F41klDkH6K7uMVDduaYeOd5Oyeh6jKD6c8PvzaOSDk4LkMMloxnklkh%2Fi8qI9Vk5z1ejCoOevCW%2FulrMwMgZuU6NyNpTCNiJ7FBjqwAWDNxm0oyrgHd2eFbPSi8I6bJoc2fXszPeluZOplg0o6E7%2BFC6rUMPpY6Dmi6AEJEq%2B2VIBGxl7Ar8%2BEPuDAV319CVpwV1%2BlsCzHYei%2BNuOZXlSx4iX8P%2FYad%2FEuZWRciI99UcqeeKYGjADrKlv9jG2OUP%2BIxe5TqmCPU6YuWeBk94BByLWeIPbPsG%2FUTx4hgvUz3uSz4XsAN8ptiVf5KCzKu8B5XJzPuC%2BnFVXwo5JF&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250821T211337Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYUGNQQUPX%2F20250821%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=c523b6f24479335e6b721082ebe8d26c7fd98810966273b1d42e29399da4b29a&hash=7b1bd8ecabba0d3927c6b9d7a42eb2e3118d12aa32bc848d763630c30f72b0f4&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S1053811921008466&tid=spdf-a765b0bf-8234-4fcd-a238-30c3689fa3dc&sid=39528439443a5141ab78651427de0c469842gxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&rh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=1b1a575155035452025a&rr=972d22a5dad0cfbb&cc=au

    # https://doi.org/10.1523/eneuro.0334-16.2016
    # https://www.eneuro.org/content/eneuro/3/6/ENEURO.0334-16.2016.full.pdf

    # https://doi.org/10.1016/j.neuroimage.2019.116178
    # https://pdf.sciencedirectassets.com/272508/1-s2.0-S1053811919X00154/1-s2.0-S1053811919307694/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEK3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIBkY4pDqK%2FdNCtcxAcHCRHS8fOsOEzK1aZxwOLRzLD%2BFAiBzRTiyykWiS22B%2BZ7jDlINENJHytfJueaVltMC1EYPvSq7BQj1%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAUaDDA1OTAwMzU0Njg2NSIMMTkY0jOt%2FbdL%2FIohKo8FRRm5uSk0vZSU0m7ZeZMR96khTGQxhRl%2FplpzNlDpw6NEdhHYiTwSnGi84t9aOMYNmz8TB43vjnfJ3YmxApWhyNK39HiVTtuzv2ujQT8bwNCj8%2BMHmblRDHnQcn%2F5PnGBjmPUkzBT3inl3zYKGT3VcKBdHckrInLZD7xeEFmjUa42nIExTwoJ7ngig926XxFHddFp4G2tTxKpp9jp0XCP1DKpemdTWyveqC4m1TZMZ1qjZPkQF%2FRyxlCofdHmVUzFGSsWUl6iHgwWoqMISm0y5SRHwleQUHrmEx8I3cak9zeim3NCHlwDGPz8OTmzS7keZCPVqHMqDvkWYDsT3%2BHsbBWRmju8Llmid7R26LE9Wy%2BtlL%2BmrB1ON46Rv01dkeSdeslPjdBJ8q5niHwFnpsQVmpnxcWmCy03xNrjEirluu4jc%2BKAWabiVtjREB3s0TAGN9q0cykW1QA9Gp9y2FEoK9HIE3OL6JgUvLq30ql%2Bwy49cv6Q0xA%2FfXohHbpnX2Jh75%2BWNaK3dELUxQFXBWfSJUUxjrXFL%2F5Ve0598EJHDZKiLKwkIldVHYgB9LG8b0ja7bP5znnYND0MHuZRNLQUbLRmxp9q9aD6vQovNjLyka9nD39EgDXHD6m2%2Fh4GmacXPoZ%2F%2BknaKJITmYL00abd2JY5mhC1xiosLLd29HwwpeJ3fAbP4cP7d4IqV4he%2BrxCXOcLhXrTgFBxIiX303rFfY88QVl7l6sHRn6hFJMPQi9dpAw9CtqMbhne5YTXWp59wygh4sZoRJ1Ark409okqji1kSTzC7ncb%2BD%2BJh7n7XmoAD8gqlnW8pT1vvlfLIfOGObqbGzokaUQF5fE%2FPKiifNYWJQ0FEuJ6rACcJptamDC%2B%2Bp3FBjqyAVvoerBridFKX0Oeukb99Q9%2BOQPNyqUp2a6cIqsCe%2BUmxYi7BpTiCymfPpNfXLv%2BF3NPOU85gD2gmFfSxiKNM1JXMcnMRlz8uhRslLa7NeXLZIvzXeaaV%2BaB%2Bm%2F1t%2FR8l5xJCX%2F7ur%2FUd2nK6RlgrlAbcjLAx%2BkucEB2OdrbYe9rf8w6ijem6z%2FNSD9znKmRTk21Oonr1oOiGDNAdsCQagM35eTjn2O%2BXruhVZhUTDU9fUo%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250821T211428Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTY6S63PFP3%2F20250821%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=2dc4ba73819adb742e29639308c4bc56b10036f904270da3a1ed3f7e24516c2b&hash=d12f0504cd53feb9f7fd767b3b8ae4ead2506f09cecff152423cd302883ef604&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S1053811919307694&tid=spdf-9e6c1bdb-98fb-4667-a858-f18b37680e89&sid=39528439443a5141ab78651427de0c469842gxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&rh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=1b1a575155035453065f&rr=972d23e03d1ccfbb&cc=au

    parser.add_argument(
        "--no-cache",
        "-nc",
        action="store_true",
        default=False,
        help="Disable caching for URL finder (default: %(default)s)",
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys

    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_01-url.py  --no-cache

# EOF
