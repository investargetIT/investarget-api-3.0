#coding=utf-8

MESSAGE_DICT = {
    'systemrecommendproject':{
        "sms_sign": "lV0m62",
        "email_sign": "SRo1Y1",
        'title_cn' : '系统项目推荐',
        'title_en' : 'You have got a new recommended project',
        'content_cn' : '根据您的意向，系统向您推荐【%s】。',
        'content_en' : 'According to your investment criterion, InvesTarget recommended Project to you:【%s】.',
        'messagetype': '1',
    },
    'traderrecommendproject':{
        "sms_sign": "S588p2",
        "email_sign": "quyk52",
        'title_cn' : '交易师项目推荐',
        'title_en' : 'You have got a new recommended project',
        'content_cn' : '您的交易师%s推荐给您项目【%s】。',
        'content_en' : 'According to your investment criterion, Transaction Manager %s recommended Project to you:【%s】.',
        'messagetype': '2',
    },
    'investorinvestproject':{
        "sms_sign": "JzW3h",
        "email_sign": "LQrMB1",
        'title_cn' : '您的投资者对项目感兴趣',
        'title_en' : 'Your investor has interests in project',
        'content_cn' : '您的投资者%s对项目【%s】感兴趣，请在48小时内联系投资者。',
        'content_en' : 'Your investor %s has interests in project 【%s】, please contact your investor in 48 hours',
        'messagetype': '3',
    },
    'traderadd': {
        'sms_sign': "pT0yA4",
        'email_sign': "X6JEv3",
        'title_cn': "交易师已添加",
        'title_en': "Your Transaction Manager has been assigned",
        'content_cn': "已为您添加交易师%s，感谢您的信任与支持！",
        'content_en': "You have been assigned for new Transaction Manager %s. Thank you for your trust and support in InvesTarget!",
        'messagetype': '4',
    },
    'userauditpass':{
        'sms_sign': "EXIDv1",
        'email_sign': "uszOI1",
        'title_cn': "申请已经通过审核",
        'title_en': "Application has been approved",
        'content_cn': "您申请的【%s】的【%s】已经通过审核，欢迎使用平台为您提供的服务。",
        'content_en': "Your application for【%s】on the 【%s】 platform has been approved. Please enjoy our services by continue using our platform.",
        'messagetype': '5',
    },
    'userauditunpass':{
        'sms_sign': None,
        'email_sign': "ZNRYV3",
        'title_cn': "申请未通过审核",
        'title_en': "Application has not been approved",
        'content_cn': "抱歉，您申请的【%s】的【%s】未通过审核，请您重新登录并修改信息。另外我们的工作人员也将尽快与您取得联系，指导您进行下一步操作。",
        'content_en': "We are sorry to inform you that your application for 【%s】 on the 【%s】 platform has not been approved. Please log in and revise the information you have provided. Our staff will be in contact shortly and guide you through the next step of operation. Thank you for your patience.",
        'messagetype': '5',
    },
    'userregister':{
        'sms_sign': None,
        'email_sign': "J6VK41",
        'title_cn': "申请将在24小时内完成审核",
        'title_en': "Application will be examined and verified in 24 hours",
        'content_cn': "您申请的【%s】的【%s】将在24小时内完成审核，请继耐心等待后续通知。",
        'content_en': "Your application for 【%s】 on the 【%s】 platform will be examined and verified within a 24-hour period. Please wait for further notice. Thank you for your patience.",
        'messagetype': '5',
    },



    'timelineauditstatuchange':{
        'sms_sign': "tNEV93",
        'email_sign': "LkZix2",
        'title_cn': "时间轴状态更新",
        'title_en': "Timeline status updates notification",
        'content_cn': "您的项目【%s】时间轴状态已更新，点击查看最新状态",
        'content_en': "Your project 【%s】 has a new status, you can review the update after logging in",
        'messagetype': '6',
    },

    # 'dataroomfileupdate':{
    #     "template_code": "SMS_33590296",
    #     "title": "DataRoom文件更新通知,DataRoom updates notification",
    #     "content": "您关注的{0}项目DataRoom有文件更新，请登录后查看详情。DataRoom for Project {1} that you are following has new updates, please log in for more details."
    #
    # },

    'projectpublish':{
        'sms_sign': None,
        'email_sign': "IszFR1",
        'title_cn': "项目已经发布,",
        'title_en': "Project  has been published",
        'content_cn': "【%s】项目已通过终审并在平台发布，可在登录后查看项目进展情况。",
        'content_en': "Project【%s】 has been verified and published on our platform, you can see the progress after logging in.",
        'messagetype': '7',
    },

    'usermakefriends':{
        'sms_sign': None,
        'email_sign': None,
        'title_cn': "好友申请",
        'title_en': "A friend application",
        'content_cn': "您有一个好友添加申请",
        'content_en': "You have a friend application",
        'messagetype': '8',
    },

    'timelinealertcycleexpire':{
        'sms_sign': None,
        'email_sign': None,
        'title_cn': "时间轴到期",
        'title_en': "Timeline issue",
        'content_cn': "您有一个项目时间轴提醒今天到期",
        'content_en': "You have a project timeline to remind issue today",
        'messagetype': '9',
    },

    'schedulemsg':{
        'sms_sign': None,
        'email_sign': None,
        'title_cn': "日程到期",
        'title_en': "Schedule issue",
        'content_cn': "您有一个日程今天到期",
        'content_en': "You have a schedule issue today",
        'messagetype': '10',
    },
    'orgBDMessage':{
        'sms_sign': "M2d4Q3",
        'email_sign': None,
        'title_cn': "机构BD任务",
        'title_en': "Schedule issue",
        'content_cn': "项目【%s】有新的BD任务分配给您，请查看",
        'content_en': "Project【%s】has a new BD task for you,please check in the system",
        'messagetype': '11',
    },
    'orgBdExpire':{
        'sms_sign': None,
        'email_sign': '8gPeo',
        'title_cn': "机构BD过期提醒",
        'title_en': "Schedule issue",
        'content_cn': "您有一个机构BD任务即将过期",
        'content_en': "You have a BD issue of organization will be expired",
        'messagetype': '11',
    },
}
