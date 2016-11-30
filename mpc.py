# coding: utf-8

#
#    *************           *************            *************
#    *  client   *           *   client  *            *   client  *
#    *************           *************            *************
#          |                        |                        |
#          |                        |                        |
#     *************          **************          **************
#     * websocket *          *  websocket *          *  websocket *
#     *    HUB    *          *     HUB    *          *      HUB   *
#     *************          **************          **************
#           \ sub                |  sub              sub/
#            \                   |                     /
#              ------------------|--------------------
#                                | pub
#                         ****************
#                         *              *
#                         *     MPC      *
#                         *              *
#                         ****************
#                                | sub
#              ------------------|-------------------
#            /                   |                    \
#          /                     |                      \
#     ***********            **********               ************
#     * sdk     *            * sdk    *               * sdk      *
#     * service *            * http   *               * other... *
#     ***********            **********               ************
#
u"""
MPC 消息发布中心
接受sdk发布的消息,并转发到gateway的消息hub上

python mpc.py -s 5559 -p 5560
"""

import getopt
import sys
import logging
import zmq

def serv_forever(sub_p, pub_p):

    try:
        context = zmq.Context()
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind('tcp://*:{}'.format(sub_p))
        
        frontend.setsockopt(zmq.SUBSCRIBE, '')
        
        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind('tcp://*:{}'.format(pub_p))

        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception, e:
        print 'bringing down zmq device'
        raise e
    finally:
        frontend.close()
        backend.close()
        context.term()


if __name__ == "__main__":
    sub_p = 5559
    pub_p = 5560
    opts, argvs = getopt.getopt(sys.argv[1:], 's:p:')
    for op, value in opts:
        if op == '-s':
            sub_p = int(value)
        if op == '-p':
            pub_p = int(value)
    logging.info('starting...')
    serv_forever(sub_p, pub_p)