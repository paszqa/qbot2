
# qbot2
qBot2 / qqBot / Discord Gaming Tracking Bot

It's still a work in progress and the documentation is not ready.

config.json file should be put in the main directory

# An example config.json file
    {
    	"token": "ENTER DISCORD TOKEN HERE",
    	
    	"logging_level" : 1,
    	
    	"script_path" : "/home/pi/qbot2/",
    	
    	"dbhost": "localhost",
    	"dbuser": "loser",
    	"dbpass": "dupa",
    	"dbname": "qqbot",
    	
    	"qbot_user_id" : "ENTER DISCORD USER ID OF THE BOT",
    	
    	"answers" : {
    		"qqbot" : "Answer\nLine" ,
    		"hello" : "Hey",
    		"testmessage" : "test Answer 123"
    	},
    	
    	"image_extra_text" : "Don't worry.",
    	
    	"price_enabled" : true,
    	"price_path" : "modules/gameprice/",
    	"price_print_link" : true,
    	"price_command" : "qprice",
    	
    	
    	"releases_path" : "modules/newreleases/",
    	"new_releases_enabled" : true,
    	"new_releases_command" : "qnew",
    	"soon_releases_enabled" : true,
    	"soon_releases_command" : "qsoon",
    	"year_releases_enabled" : false,
    	"year_releases_command" : "q6m",
    	
    	"steam_sum_up_path" : "modules/steamsumup/",
    	"steam_sum_up_enabled" : true,
    	"steam_api_key" : "ENTER_STEAM_API_KEY",
    	"steam_id_for_api_key" : "ENTER_STEAM_ID_THE_API_KEY_BELONGS TO",
    	
    	"userdata_path" : "modules/userdata/",
    	"userdata_add_steam_enabled" : true,
    	"userdata_add_steam_command" : "linksteam",
    	"userdata_add_twitch_enabled" : true,
    	"userdata_add_twitch_command" : "linktwitch",
    	
    	"twitch_api_client_id" : "ENTER_IT_HERE",
    	"twitch_api_secret" : "ENTER_IT_HERE",
    	"igdb_api_client" : "ENTER_IT_HERE",
    	"igdb_api_token" : "ENTER_IT_HERE",
    	
    	"activity_path" : "modules/activity/",
    	"activity_debug_enabled" : true,
    	"activity_debug_command" : "debugactivity",
    	"activity_schedule_enabled" : true,
    	"activity_schedule_cron" : "0 */5 * * * *",
    	"activity_schedule_cron_tick" : "5",
    	
    	"activity_image_title" : "Last week on the server...",
    	"activity_image_channel" : "ENTER CHANNEL ID WHERE TO PASTE THE ACTIVITY IMAGE EVERY WEEK",
    	
    	"votesystem_path" : "modules/votesystem/",
    	"votesystem_enabled" : true,
    	"votesystem_add_vote_option_command" : "qaddvote",
    	"votesystem_add_vote_admin_user_id" : "ENTER USER ID OF USER THAT CAN MANAGE VOTE SYSTEM",
    	"votesystem_debug_command" : "qdebugvote",
    	"votesystem_channel" : "ENTER CHANNEL ID WHERE VOTING HAPPENS",
    	
    	"year_recap_path" : "modules/year-recap/",
    	
    	"gamename_path" : "modules/gamename/"
    }

