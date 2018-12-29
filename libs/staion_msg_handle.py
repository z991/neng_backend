# __author__='gzh'

import json
import logging
from rest_framework import status
from rest_framework.response import Response
from common.custom_exception import PushError
from libs.classic_service.site_push import infopush
from libs.push_service_cg.push_service import Push_manage
logger = logging.getLogger('django')


def station_msg_push(station_id,online_status,station_classify):
    # kf_10087    False     1
    if station_classify == 1:
        # 经典版推送
        try:
            resp = infopush(station_id, online_status)
        except Exception as e:
            raise PushError("11"+str(e))
        else:
            resp = json.loads(resp.content.decode('utf-8'))
            logger.info('企业id：' + str(station_id) + '----状态：' +str(online_status)+ '----推送信息' + str(resp['status']) + str(resp['error']))
            if not resp['status']:
                raise PushError('msg push fail')
            else:
                return Response({}, status=status.HTTP_200_OK)
    else:
        # 重构版本推送
        logger.debug('------------------------------------------------------')
        #res = tasks.add_task.delay(station_id,'cg')
        data = Push_manage(station_id, 'cg',online_status).push_data()
        logger.debug('------------------------------------------------------')
        return Response({}, status=status.HTTP_200_OK)