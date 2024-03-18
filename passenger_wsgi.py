import os
import sys
import asyncio


sys.path.insert(0, os.path.dirname(__file__))


def application(environ, start_response):
    import main
    asyncio.run(main.bot.polling())
    start_response('200 OK', [('Content-Type', 'text/plain')])
    message = 'It works!\n'
    version = 'Python %s\n' % sys.version.split()[0]
    response = '\n'.join([message, version])
    return [response.encode()]
