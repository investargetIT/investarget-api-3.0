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
    "traderadd": {
        "sms_sign": "pT0yA4",
        "email_sign": "X6JEv3",
        "title_cn": "交易师已添加",
        "title_en": "Your Transaction Manager has been assigned",
        "content_cn": "已为您添加交易师%s，感谢您的信任与支持！",
        "content_en": "You have been assigned for new Transaction Manager %s. Thank you for your trust and support in InvesTarget!",
        'messagetype': '4',
    },
    "userauditpass":{
        "sms_sign": "EXIDv1",
        "email_sign": "uszOI1",
        "title_cn": "申请已经通过审核",
        "title_en": "Application has been approved",
        "content_cn": "您申请的Investarget海拓的【%s】已经通过审核，请继续使用海拓平台为您提供的服务。",
        "content_en": "Your application for【%s】on the InvesTarget platform has been approved. Please enjoy our services by continue using our platform.",
        'messagetype': '5',
    },
    "userauditunpass":{
        "sms_sign": None,
        "email_sign": "ZNRYV3",
        "title_cn": "申请未通过审核",
        "title_en": "Application has not been approved",
        "content_cn": "抱歉，您申请的Investarget海拓的【%s】未通过审核，请您重新登录并修改信息。另外我们的工作人员也将尽快与您取得联系，指导您进行下一步操作。",
        "content_en": "We are sorry to inform you that your application for 【%s】 on the InvesTarget platform has not been approved. Please log in and revise the information you have provided. Our staff will be in contact shortly and guide you through the next step of operation. Thank you for your patience.",
        'messagetype': '5',
    },
    "userregister":{
        "sms_sign": None,
        "email_sign": "J6VK41",
        "title_cn": "申请将在24小时内完成审核",
        "title_en": "Application will be examined and verified in 24 hours",
        "content_cn": "您申请的Investarget海拓的【%s】将在24小时内完成审核，请继耐心等待后续通知。",
        "content_en": "Your application for 【%s】 on the InvesTarget platform will be examined and verified within a 24-hour period. Please wait for further notice. Thank you for your patience.",
        'messagetype': '5',
    },



    "timelineauditstatuchange":{
        "sms_sign": "tNEV93",
        "email_sign": "LkZix2",
        "title_cn": "交易师已添加",
        "title_en": "Your Transaction Manager has been assigned",
        "content_cn": "已为您添加交易师%s，感谢您的信任与支持！",
        "content_en": "You have been assigned for new Transaction Manager %s. Thank you for your trust and support in InvesTarget!",
        'messagetype': '6',
    },

    # "dataroomfileupdate":{
    #     "template_code": "SMS_33590296",
    #     "title": "DataRoom文件更新通知,DataRoom updates notification",
    #     "content": "您关注的{0}项目DataRoom有文件更新，请登录后查看详情。DataRoom for Project {1} that you are following has new updates, please log in for more details."
    #
    # },

    "projectpublish":{
        "sms_sign": None,
        "email_sign": "IszFR1",
        "title_cn": "您的项目已经发布,",
        "title_en": "Your project  has been published",
        "content_cn": "您上传的【%s】项目已通过终审并在平台发布，可在登录后查看项目进展情况。",
        "content_en": "Project【%s】 has been verified and published on our platform, you can see the progress after logging in.",
        'messagetype': '7',
    },

    "usermakefriends":{
        "sms_sign": None,
        "email_sign": None,
        "title_cn": "好友申请,",
        "title_en": "A friend application",
        "content_cn": "您有一个好友添加申请",
        "content_en": "You have a friend application",
        'messagetype': '8',
    },

    "timelinealertcycleexpire":{
        "sms_sign": None,
        "email_sign": None,
        "title_cn": "时间轴到期,",
        "title_en": "Timeline due",
        "content_cn": "您有一个项目时间轴提醒今天到期",
        "content_en": "You have a project timeline to remind due today",
        'messagetype': '9',
    },

    "schedulemsg":{
        "sms_sign": None,
        "email_sign": None,
        "title_cn": "日程到期,",
        "title_en": "Schedule due",
        "content_cn": "您有一个日程今天到期",
        "content_en": "You have a schedule due today",
        'messagetype': '10',
    },
    "orgBDMessage":{
        "sms_sign": "M2d4Q3",
        "email_sign": None,
        "title_cn": "机构BD,",
        "title_en": "Schedule due",
        "content_cn": "您有一个新机构BD任务",
        "content_en": "You have a schedule due today",
        'messagetype': '11',
    },
}


aaa = {
    "Investor": {
        "dataRoomUpdate": {
            "template_code": "SMS_33590296",
            "Title": "DataRoom文件更新通知,DataRoom updates notification",
            "Message": "您关注的{0}项目DataRoom有文件更新，请登录后查看详情。DataRoom for Project {1} that you are following has new updates, please log in for more details."
        },
        "ProjectRecommendedByTransaction": {
            "template_code": "SMS_8920868",
            "Title": "您有新的项目信息,You have got a new recommended project",
            "Message": "根据您的投资意向，交易师{0}向您推荐{1}。请登录后查看详情。According to your investment criterion, Transaction Manager {2} recommended Project to you:{3}’ history. Please log in to for more details."
        },
        "ProjectRecommendedBySystem": {
            "template_code": "SMS_33570397",
            "Title": "您有新的项目信息,You have got a new recommended project",
            "Message": "根据您的投资意向，多维海拓向您推荐{0}。请登录后查看详情。According to your investment criterion, InvesTarget  recommended Project  to you:{1}’ history. Please log in to for more details."
        },

        "ChangeTransaction": {
            "template_code": "SMS_33645367",
            "Title": "您的交易师已更换,Your Transaction Manager has been changed",
            "Message": "您的交易师已更换为{0}。感谢您对海拓交易平台的信任与支持！{1} is now your new Transaction Manager. Thank you for your trust and support in InvesTarget!"
        }
    },
    "Supplier": {
        "dataRoomUpdate": {
            "template_code": "SMS_33590296",
            "Title": "DataRoom文件更新通知,Project status updates notification",
            "Message": "您{0}项目DataRoom有文件更新，请登录后查看详情。The DataRoom for Project {1} has been updated, please log in for more details."
        },
        "InvestorfollowedProject": {
            "template_code": "SMS_8920868",
            "Title": "有投资人收藏了您的项目,New investors have followed your project",
            "Message": "投资人{0}收藏了您的{1}项目 。请及时登录联系投资人。Investor {2} followed Project {3}. Please log in and take the chance to contact the investor as soon as possible."
        },
        "ProjectStatusUpdate": {
            "template_code": "SMS_33655204",
            "Title": "项目状态更新通知,Project status updates notification",
            "Message": "您上传的项目状态已经更新，可在登录后查看项目最新状态。Your project has a new status, you can review the update after logging in."
        },
        "ProjectPublished": {
            "template_code": "SMS_8495019",
            "Title": "您的项目已经发布,Your project  has been published",
            "Message": "您上传的{0}项目已通过终审并在平台发布，可在登录后查看项目进展情况。Project {1} has been verified and published on our platform, you can see the progress after logging in."
        }
    },
    "Transaction": {
        "InvestorContract": {
            "template_code": "SMS_8975636",
            "Title": "投资人{0}给您发送了新消息,Investor {1} sent you a message",
            "Message": "投资人{0}给您发送了新消息，请登录后查看详情。Investor {1} sent you a message, please log in for more details."
        },
        "InvestorfollowedProject": {
            "template_code": "SMS_8920868",
            "Title": "有投资人收藏了您的项目,New investors  followed your project",
            "Message": "投资人{0}收藏了您的{1}项目 。请及时登录联系投资人。Investor {2} followed Project {3}. Please log in and take the chance to contact the investor as soon as possible."
        },
        "dataRoomUpdate": {
            "template_code": "SMS_33590296",
            "Title": "DataRoom文件更新通知,Project status updates notification",
            "Message": "您{0}项目DataRoom有文件更新，请登录后查看详情。DataRoom for Project {1} that you are following  has been updated, please log in for more details."
        },
        "ProjectStatusUpdate": {
            "template_code": "SMS_33655204",
            "Title": "项目状态更新通知,Project status updates notification",
            "Message": "您的{0}项目状态已更新，请登录后及时查看最新状态。Your project {1} has a new status, you can review the update after logging in."
        }
    }

}





bbb = {
    "userApply": {
        "template_code": "SMS_8495019",
        "Title_cn": "申请将在24小时内完成审核",
        "Title_en": "Application will be examined and verified in 24 hours",
        "Message_cn": "您申请的Investarget海拓的【{0}】将在24小时内完成审核，请继耐心等待后续通知。",
        "Message_en": "Your application for {0} on the InvesTarget platform will be examined and verified within a 24-hour period. Please wait for further notice. Thank you for your patience.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>您申请的Investarget海拓的【{0}】将在24小时内完成审核，请继耐心等待后续通知。Your application for {1} on the InvesTarget platform will be examined and verified within a 24-hour period. Please wait for further notice. Thank you for your patience.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    },
    "userPass": {
        "template_code": "SMS_8530018",
        "Title_cn": "申请已经通过审核",
        "Title_en": "Application has been approved",
        "Message_cn": "您申请的Investarget海拓的【{0}】已经通过审核，请继续使用海拓平台为您提供的服务。",
        "Message_en": "Your application for {0} on the InvesTarget platform has been approved. Please enjoy our services by continue using our platform.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>您申请的Investarget海拓的【{0}】已经通过审核，请继续使用海拓平台为您提供的服务。Your application for {1} on the InvesTarget platform has been approved. Please enjoy our services by continue using our platform.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    },
    "userNotPass": {
        "template_code": "SMS_8475034",
        "Title_cn": "申请未通过审核",
        "Title_en": "Application has not been approved",
        "Message_cn": "抱歉，您申请的Investarget海拓的【{0}】未通过审核，请您重新登录并修改信息。另外我们的工作人员也将尽快与您取得联系，指导您进行下一步操作。",
        "Message_en": "We are sorry to inform you that your application for {0} on the InvesTarget platform has not been approved. Please log in and revise the information you have provided. Our staff will be in contact shortly and guide you through the next step of operation. Thank you for your patience.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>抱歉，您申请的Investarget海拓的【{0}】未通过审核，请您重新登录并修改信息。另外我们的工作人员也将尽快与您取得联系，指导您进行下一步操作。We are sorry to inform you that your application for {1} on the InvesTarget platform has not been approved. Please log in and revise the information you have provided. Our staff will be in contact shortly and guide you through the next step of operation. Thank you for your patience.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    },
    "ProjectUpload": {
        "template_code": "SMS_8530557",
        "Title_cn": "项目将在48小时内完成审核",
        "Title_en": "Project will be examine and verified in 48 hours",
        "Message_cn": "您上传到Investarget海拓的项目[{0}]将在48小时内完成审核，请耐心等待后续通知。",
        "Message_en": "Your upload of project[{0}] on the InvesTarget platform has been received and will be examined and verified within a 48-hour period. Please wait for further notice. Thank you for your patience.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>您上传到Investarget海拓的项目[{0}]将在48小时内完成审核，请耐心等待后续通知。Your upload of project[{1}] on the InvesTarget platform has been received and will be examined and verified within a 48-hour period. Please wait for further notice. Thank you for your patience.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    },
    "RequirementUpload": {
        "template_code": "SMS_8530557",
        "Title_cn": "需求将在48小时内完成审核",
        "Title_en": "Demand will be examine and verified in 48 hours",
        "Message_cn": "您上传到Investarget海拓的需求[{0}]将在48小时内完成审核，请耐心等待后续通知。",
        "Message_en": "Your upload of demand [{0}] on the InvesTarget platform has been received and will be examined and verified within a 48-hour period. Please wait for further notice. Thank you for your patience.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>您上传到Investarget海拓的需求[{0}]将在48小时内完成审核，请耐心等待后续通知。Your upload of demand [{1}] on the InvesTarget platform has been received and will be examined and verified within a 48-hour period. Please wait for further notice. Thank you for your patience.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    },
    "ProjectPass": {
        "template_code": "SMS_8930912",
        "Title_cn": "项目已经完成审核",
        "Title_en": "Project has been examined and approved",
        "Message_cn": "您上传到Investarget海拓的项目[{0}]已经完成审核,请继续使用海拓平台为您提供的服务。",
        "Message_en": "Your upload of project[{0}] on the InvesTarget platform has been examined and approved. Please enjoy our services by continue using our platform.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>您上传到Investarget海拓的项目[{0}]已经完成审核，请继续使用海拓平台为您提供的服务。Your upload of project[{1}] on the InvesTarget platform has been examined and approved. Please enjoy our services by continue using our platform.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    },
     "RequirementPass": {
        "template_code": "SMS_8930912",
        "Title_cn": "需求已经完成审核",
        "Title_en": "Demand has been examined and approved",
        "Message_cn": "您上传到Investarget海拓的需求[{0}]已经完成审核,请继续使用海拓平台为您提供的服务。",
        "Message_en": "Your upload of demand [{0}] on the InvesTarget platform has been examined and approved. Please enjoy our services by continue using our platform.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>您上传到Investarget海拓的需求[{0}]已经完成审核，请继续使用海拓平台为您提供的服务。Your upload of demand [{1}] on the InvesTarget platform has been examined and approved. Please enjoy our services by continue using our platform.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    },
    "ProjectRecommended": {
        "template_code": "SMS_8920868",
        "Title_cn": "您的交易师{0}推荐给您项目{1}",
        "Title_en": "project {1} has been recommended to the favorite by your transaction manager{0}",
        "Message_cn": "您的交易师{0}推荐给您项目{1},请登录后查看详情。",
        "Message_en": "You transaction manager {0} has recommended you this project{1} posted on the InvesTarget platform. Please log in for more details.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>您的交易师{0}推荐给您项目{1},请登录后查看详情。You transaction manager {0}has recommended you this project {2} posted on the InvesTarget platform. Please log in for more details.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    },
    "ProjectInterest": {
        "template_code": "SMS_8975636",
        "Title_cn": "您的投资者{0}对{1}项目感兴趣",
        "Title_en": "Your investor {0} on Investarget has interests in project {1}, please contact your investor in 48 hours",
        "Message_cn": "您的投资者{0}对{1}项目感兴趣,请在48小时内联系投资者,登录后查看详情。",
        "Message_en": "Your investor {0} is interested in this project {1} posted on the InvesTarget platform. Please contact the investor within a 48-hour period. Please log in for more details.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>您的投资者{0}对{1}项目感兴趣,请在48小时内联系投资者,请登录后查看详情。Your investor{0}is interested in this project {2} posted on the InvesTarget platform. Please contact the investor within a 48-hour period. Please log in for more details.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    },
    "ProjectFavorited": {
        "template_code": "SMS_8935896",
        "Title_cn": "有投资者对您的项目感兴趣",
        "Title_en": "investor has interest in the project you uploaded",
        "Message_cn": "有投资者对Investarget海拓的项目{0}感兴趣，请登录后查看详情。",
        "Message_en": "An investor is interested in this project {0} posted on the InvesTarget platform. Please log in for more details.",
        "Message_html": "<!doctype html><html><head><meta charset='GB2312'><title></title></head><body><table><tr><h3 style='padding-left: 50px'>您好，</tr><tr><h3 style='padding-left: 50px'>有投资者对Investarget海拓的项目（{0}）感兴趣，请登陆后查看详情。An investor is interested in this project {1} posted on the InvesTarget platform. Please log in for more details.</h3></tr><tr><img src='http://7xrq1y.com2.z0.glb.qiniucdn.com/registerBottom.png'></tr></table></body></html>"
    }

}
