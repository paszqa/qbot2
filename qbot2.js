////////////////////////// 
// qqBot / qBot2 by Paszq
// 2022
// v0.1.0		2022-03-21		Paszq		Built on top of qBot v0.5.0, 
//											modules: getPrice, newreleases
////////////////////////// 

////////////////////////// 
// Requires
////////////////////////// 
const Discord = require("discord.js");
var logger = require('winston');
const client = new Discord.Client();
var config = require('./config.json');
var cron = require("node-cron");
var mysql = require('mysql');

//////////////////////////
// DB
//////////////////////////
var con = mysql.createConnection({
  host: "localhost",
  user: "loser",
  password: "dupa",
  database: "qqbot"
});

//////////////////////////
// Running the bot, initialization on launch
//////////////////////////
client.on("ready", () => {
    console.log("I am ready!");
    console.log(client.user.tag + ' ///// ' + client.user.id);
	enableCronJobs(); // Enables scheduled jobs on start
	con.connect
});

//////////////////////////
// Running the bot, listening for messages
//////////////////////////
client.on("message", (message) => {
    if (message.content.startsWith("!")) {
        var args = message.content.substring(1).split(' ');
        var cmd = args[0];
		if(config.answers.hasOwnProperty(cmd)){
			message.channel.send("q "+config.answers[cmd]);
		}
		else if(config.price_command == cmd && config.price_enabled){
			getGamePrice(args.slice(1).join(' '), message);
		}
		else if(config.new_releases_command == cmd && config.new_releases_enabled){
			showReleasesImageToChannel(message.channel, "new"); // show recently released games
		}
		else if(config.soon_releases_command == cmd && config.soon_releases_enabled){
			showReleasesImageToChannel(message.channel, "month"); // show games coming out in the next month
		}
		else if(config.userdata_add_steam_command == cmd && config.userdata_add_steam_enabled){
			addUserdata(message, "steam");
		}
		else if(config.userdata_add_twitch_command == cmd && config.userdata_add_twitch_enabled){
			addUserdata(message, "twitch");
		}
		else if(cmd == "debugactivity"){
			logActivity();
		}
		else if(config.votesystem_add_vote_option_command == cmd && config.votesystem_enabled){
			createVotingMessage(message);
		}
		else if(cmd == "debugvote"){
			addVotingOptionToDatabase(message);
			//checkReactions("966088539169247353");
		}
		else if(cmd == "debugdb"){
			getVotePostsFromDatabase();
		}
		else if(cmd == "debugmissing"){
			createMissingMessagesFromDB();
		}
		else if(cmd == "debugrecreate"){
			recreateReactionsForAllVotingOptions();
		}
		else if(cmd == "recap2023"){
			postRecap(config.year_recap_image_channel);
		}
        //switch (cmd) {
            //case "qqbot":
                //message.channel.send(config.qbot);
                //break;
		//}
    }
});
///////////////////////////////////////////
/////////////////////////// DATE
///////////////////////////////////////////
function ReturnDate(){
	d = new Date();
	year = d.getFullYear();
	month = d.getMonth() + 1;
	if(month < 10){
		month = "0" + month;
	}
	day = d.getDate();
	if(day < 10){
		day = "0" + day;
	}
	hours = d.getHours();
	if(hours < 10){
		hours ="0" + hours;
	}
	minutes = d.getMinutes();
	if(minutes < 10){
		minutes = "0" + minutes;
	}
	seconds = d.getSeconds();
	if(seconds < 10){
		seconds = "0" + seconds;
	}
	return "["+year+"-"+month+"-"+day+" "+hours+":"+minutes+":"+seconds+"]";
}

///////////////////////////////////////////
////////////////////////// GAME PRICE STUFF
///////////////////////////////////////////

function getGamePrice(args, message){ //take all arguments and the message
        console.log(ReturnDate()+" [INFO] Started getGamePrice() using command: "+'python3 '+config.script_path+config.price_path+'getPrice.py "'+args+'"');
        const { exec } = require('child_process');
        exec('python3 '+config.script_path+config.price_path+'getPrice.py "'+args+'"', (err, stdout, stderr) => { //Put all arguments within ' ' and run Python script with it
                if (err) {
                        console.log(ReturnDate()+" [ERROR] Error checking price for args: "+args)
                        message.channel.send("Error checking price.");  //Inform about the error in a message
                } else {
                        console.log(ReturnDate()+" [INFO] Checking price - "+args);
                        content = stdout.split("\n");
						message.channel.send(content, { files: [config.price_path+"/output/price.png"]}); //Paste image with price if Python script was successful
            }
        });

}



///////////////////////////////////////////
////////////////////////// ADD USERDATA STUFF
///////////////////////////////////////////

function addUserdata(message, datatype){
	var args = message.content.substring(1).split(' ');
	var discord_user_id = message.author.id;
	var discord_username = message.author.username;
	var url = args[1];
	console.log(ReturnDate()+" [INFO] Adding user data for Discord ID: "+discord_user_id+"... args: "+args);
	addUserDataManual(message, discord_user_id, discord_username, url, datatype);
}

function addUserDataManual(message, discord_user_id, discord_username, url, datatype){
	const { exec } = require('child_process');
	//console.log(datatype+" = "+url);
	switch(datatype){
		case "steam":
			const steamurl = url
			exec('python3 '+config.script_path+config.userdata_path+'addUserData.py -d '+discord_user_id+' -u "'+discord_username+'" -L '+steamurl, (err, stdout, stderr) => { //Put all arguments within ' ' and run Python script with it
                if (err) {
                        console.log(ReturnDate()+" [ERROR] Error adding user data for: "+discord_user_id+" - Steam: "+steamurl);
						if(message){
							message.channel.send("Error adding user data.");  //Inform about the error in a message
						}
                } 
				else {
                        console.log(ReturnDate()+" [INFO] Added user data for "+discord_user_id);
                        const content = stdout.split("\n");
						if(message){
							message.channel.send("Successfully added user data.");  //Inform about success in a message
						}
				}
			});
			break;
		case "twitch":
			const twitchurl = url
			exec('python3 '+config.script_path+config.userdata_path+'addUserData.py -d '+discord_user_id+' -u "'+discord_username+'" -T '+twitchurl, (err, stdout, stderr) => { //Put all arguments within ' ' and run Python script with it
                if (err) {
                        console.log(ReturnDate()+" [ERROR] Error adding user data for: "+discord_user_id+" - Twitch: "+twitchurl);
						if(message){
							message.channel.send("Error adding user data.");  //Inform about the error in a message
						}
                } 
				else {
                        console.log(ReturnDate()+" [INFO] Added user data for "+discord_user_id);
                        const content = stdout.split("\n");
						if(message){
							message.channel.send("Successfully added user data.");  //Inform about success in a message
						}
				}
			});
			break;
		case "avatar":
			const avatarid = url
			exec('python3 '+config.script_path+config.userdata_path+'addUserData.py -d '+discord_user_id+' -u "'+discord_username+'" -a "'+avatarid+'"', (err, stdout, stderr) => { //Put all arguments within ' ' and run Python script with it
                if (err) {
                        console.log(ReturnDate()+" [ERROR] Error adding user data for: "+discord_user_id+" - Avatar: "+avatarid);
						if(message){
							message.channel.send("Error adding user data.");  //Inform about the error in a message
						}
                } 
				else {
                        console.log(ReturnDate()+" [INFO] Added user data for "+discord_user_id);
                        const content = stdout.split("\n");
						if(message){
							message.channel.send("Successfully added user data.");  //Inform about success in a message
						}
				}
			});
			break;
		default:
			console.log(ReturnDate()+" [ERROR] Wrong datatype: "+datatype);
			break;
	}	
}

///////////////////////////////////////////
////////////////////////// NEW RELEASES STUFF
///////////////////////////////////////////

function showReleasesImageToChannel(toChannel, which){
	console.log(ReturnDate()+" [INFO] Sending newreleases ("+which+") to channel ID: "+toChannel+"...");
	client.channels.cache.get(""+toChannel).send("", { files: [config.releases_path+"/output/"+which+"-eng.png"]}); // Paste chosen image to channel in the parameter
}

///////////////////////////////////////////
///////////////////////// GAMES LATEST UPDATE TRACKER
///////////////////////////////////////////
function showGlutImageToChannel(toChannel, which){
	console.log(ReturnDate()+" [INFO] Sending GLUT ("+which+") to channel ID: "+toChannel+"...");
	if(which == ""){
		client.channels.cache.get(""+toChannel).send("", { files: [config.glut_path+"/output/listresult.png"]}); // Paste chosen image to channel in the parameter
	}
	else{
		sanitized_which = which.toLowerCase().replace(/[^a-z]/g, '');;
		client.channels.cache.get(""+toChannel).send("", { files: [config.glut_path+"/output/listresult-"+sanitized_which+".png"]}); // Paste chosen image to channel in the parameter
	}
}

///////////////////////////////////////////
////////////////////////// DISCORD ACTIVITY STUFF
///////////////////////////////////////////

function logActivity(){
	//message.channel.send("Count with bots: "+message.guild.memberCount);
	//console.log("MEMBERS:");
//	members = message.guild.members.fetch();
	// Get server
	const guild = client.guilds.cache.get("493082193938350080");
	//console.log(guild);
	// Fetch and get the list named 'members'
	guild.members.fetch().then(members =>
	{
	  	// Loop through members
		userCount = 0;
		members.forEach(member =>
	    	{
			if(member.user.bot){
				return;
			}
			userCount += 1;
			activityString = Date.now()+";"+member.user.username.replace(";","")+";"+member.user.id+";"+member.user.bot+";"+member.user.presence.status.replace(";"," ")+";";
			isActive = false;
			
			//Check for "playing" status
			var found = false;
			for(var j = 0; j < member.presence.activities.length;j++){
				if(member.presence.activities[j].type == 'PLAYING'){
					//console.log("Debug activity: "+member.presence.activities[j].type+" = "+member.presence.activities[j].name+" = "+member.presence.activities[j].details+" = "+member.presence.activities[j].state+" === "+member.presence.activities[j].applicationID);
					foundGame = member.presence.activities[j].name+"";
					found = true;
					isActive = true;
				}
			}
			if(!found){
				activityString += "NONE;";
			}
			else{ 
				activityString += foundGame+";";
			}
			//Check for "listening" status
			found = false;
			for(j = 0; j < member.presence.activities.length;j++){
				if(member.presence.activities[j].type == "LISTENING"){
					activityString += "music;";
					found = true;
					isActive = true;
				}
			}
			if(!found) activityString += "NONE;";
			
			//Check for "streaming" status
			found = false;
			for(j = 0; j < member.presence.activities.length;j++){
				if(member.presence.activities[j].type == "STREAMING"){
					activityString += member.presence.activities[j].state;
					//console.log(member.presence.activities[j])
					//If someone is streaming, add his Twitch channel to user data:
					addUserDataManual(null, member.user.id, member.user.username, member.presence.activities[j].url, "twitch");
					found = true;
					isActive = true;
				}
			}
			
			if(!found){
				
				//TODO: This hangs the scripts, because it launches PYTHON script for each user on the server. It needs to be consolidated and ran independently.
				//If user is not streaming on Discord, additional check Twitch API via Python script - it will add additional Activity String entry to the temp file
				/*
				*/
				//Add NONE to the standard entry of Activity String
				activityString += "NONE;";
			}
			else{ 
				activityString += ";";
			}
			//Check for avatar id
			if(member.user.avatar){
				activityString += member.user.avatar+";"
			}
			else{
				activityString += "NONE;";
			}
			console.log(isActive+";"+activityString);
			//Run python file to save info if user is active
			if(isActive){
				const { exec } = require('child_process');
				//activityStringCopy = activityString;
				const activityStringCopy = activityString;
				//This is heavy for performance for some reason if ran multiple times at once
				addUserDataManual(null, member.user.id, member.user.username, member.user.avatar, "avatar");
				exec('python3 '+config.script_path+config.activity_path+'addActivity.py "'+activityStringCopy+'"', (err, stdout, stderr) => {
					if (err) { console.error(err); }
					else {
						console.log(ReturnDate()+" [INFO] Added activity: "+activityStringCopy);
						//message.channel.send(activityStringCopy);
					}
				}); 
			}
			
		});
		//message.channel.send("User count: "+userCount);
	});
}

function logTwitchActivity(){
	const { exec } = require('child_process');
		exec('python3 '+config.script_path+config.activity_path+'checkAndAddTwitchActivity.py', (err, stdout, stderr) => {
			if (err) { console.error(err); }
			else{
				console.log(ReturnDate()+" [INFO] Scanned for Twitch activity for all users");
				
			}
	});
}
///////////////////////////////////////////
/////////////////////////// PASTE RECAP IMAGE
///////////////////////////////////////////
function postRecap(channel){
	console.log(ReturnDate()+" [INFO] Pasting activity image to channel: "+channel+"...");
	client.channels.cache.get(channel).send("", { files: [config.script_path+config.year_recap_path+"output/2023/recap.png"]}); //pastes recap image
}

///////////////////////////////////////////
/////////////////////////// PASTE ACTIVITY IMAGE
///////////////////////////////////////////
function pasteActivityImageToChannel(channel){
	console.log(ReturnDate()+" [INFO] Pasting activity image to channel: "+channel+"...");
	client.channels.cache.get(channel).send("", { files: [config.script_path+config.activity_path+"output/activity.png"]}); //pastes activity image
}

///////////////////////////////////////////
/////////////////////////// VOTE SYSTEM
///////////////////////////////////////////

function addVotingOptionToDatabase(message){
	if(message.author.id == config.votesystem_add_vote_admin_user_id){ //Allow only admin to add new votes
		arrayOfMessage = message.content.split(" ");//Split message into elements divided by spaces
		voteOption = arrayOfMessage.slice(1).join(' ');//join everything except the command (first array element)
		console.log("Vote Option: "+voteOption);
		con.query("CREATE TABLE IF NOT EXISTS `voting_options` (`id` INT(11) NOT NULL AUTO_INCREMENT,	`optionName` VARCHAR(80) NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',	`dateAdded` DATE NULL DEFAULT NULL,	PRIMARY KEY (`id`) USING BTREE) COLLATE='utf8mb4_general_ci' ENGINE=InnoDB;", function (err, result, fields) {
			con.query("SELECT * FROM `voting_options` WHERE `optionName` = '"+voteOption+"' LIMIT 1;", function (err, result, fields) {//TODO!!
				if (err){
					console.log(ReturnDate()+" [ERROR] [addVotingOptionToDatabase] Cannot run DB query: "+err);
					//con.end();
				}
				else{
					if(result.length > 0) {
						console.log(ReturnDate()+" [WARNING] An option with this name already exists in the database: "+result[0].optionName+" from "+result[0].dateAdded);
					}
					else{
						var todayDate = new Date().toISOString().slice(0, 10);
						con.query("INSERT INTO `qqbot`.`voting_options` (`optionName`, `dateAdded`) VALUES ('"+voteOption+"', '"+todayDate+"');");
						con.query("COMMIT;");
						createVotingMessageFromText(voteOption);
						console.log(ReturnDate()+" [INFO] Added voting option to database: "+voteOption+" from "+todayDate);
					}
				}
			});
		});
	}
}

//Create missing messages for vote options that have no Discord Message ID in database:
function createMissingMessagesFromDB(){
	con.query("SELECT optionName FROM `voting_options` WHERE `discordMessageId` IS NULL;", function (err, result, fields){
		if (err){
			console.log(ReturnDate()+" [ERROR] [createMissingMessagesFromDB] Cannot run DB query: "+err);
		}
		else{
			if(result.length > 0){
				for(var j = 0; j < result.length; j++){
					console.log(ReturnDate()+" [INFO] Creating a message with voting option.");
					createVotingMessageFromText(result[j].optionName);
				}
					
			}
		}
	});
	
}

//Creating new messages for vote option text:
function createVotingMessageFromText(voteOption){
	voteOption = voteOption;
	votingEntry = client.channels.cache.get(""+config.votesystem_channel).send(voteOption).then(sent => {

		let id = sent.id;
		con.query("UPDATE `qqbot`.`voting_options` SET `discordMessageId` = '"+id+"' WHERE `optionName` = '"+voteOption+"';");
		con.query("COMMIT;");
		console.log(ReturnDate()+ " [INFO] [CreateVotingMessageFromText] Added DiscordMessageID "+id+" to a DB entry for "+voteOption+".");
		//console.log(sent);
		
		const channel = client.channels.cache.get(""+config.votesystem_channel);//message.guild.channels.cache.find(ch => ch.id === config.votesystem_channel); //voting channel id
		channel.messages.fetch(id).then(rrmsg => {
			sendReactionsToMessage(rrmsg);
		}); 
	});
	console.log(ReturnDate()+ " [INFO] [CreateVotingMessageFromText] Voting entry created.");
}

//Recreate reactions for all messages from vote system
function recreateReactionsForAllVotingOptions(){
	console.log(ReturnDate()+ " [INFO] [recreateReactionsForAllVotingOptions] Running recreate function...");
	con.query("SELECT discordMessageId FROM `voting_options` WHERE `discordMessageId` IS NOT NULL;", function (err, result, fields){
		if (err){
			console.log(ReturnDate()+" [ERROR] [recreateReactionsForAllVotingOptions] Cannot run DB query: "+err);
		}
		else{
			for(var z = 0; z < result.length; z++){
				let id = result[z].discordMessageId;
				//let channel = client.channels.cache.get(""+config.votesystem_channel);
				/*
				console.log("!!!!!!!!!!!! ID: "+id);
				channel.messages.fetch(id).then(m => {
					m.react("👍");
				});
				console.log("===========================");
				console.log(channel.messages); // 3
				console.log("===========================");
				channel.messages.fetch({ limit: 90 }).then((fetchedChannel) => {
					console.log(fetchedChannel.messages); // 90
					console.log("----------------------------------------");
					//console.log(fetchedChannel.messages); // 90
				})
				;
				*/
				
				const channel = client.channels.cache.get(""+config.votesystem_channel);
				//const channel = client.channels.cache.get("890640686947381258");
				//const channel = client.channels.cache.find(ch => ch.id === config.votesystem_channel); //voting channel id
				//let abc = client.channels.cache.get("890640686947381258").message.cache.get('974658130334064661')
				//console.log("ABC: "+abc);
				//console.log("...........................");
				/*
				channel.messages.fetch('974658130334064661').then(meseg => {
					console.log("MESEG is: "+meseg);
					console.log("MESEG===========================:");
				});
				*/
				let magic = ''+'974593496839225354';
				channel.messages.fetch(magic).then(rrmsg => {
				//channel.messages.fetch(id).then(rrmsg => {
					channel.messages.fetch(id).then(contents => {
						console.log(ReturnDate()+ " [INFO] [recreateReactionsForAllVotingOptions] Triggering reaction creation for DiscordMessageID "+id+".");
						//console.log("Test:"+id);
						sendReactionsToMessage(contents);
						//console.log("REsult: "+result);
						//console.log("REsult: "+contents);
						//console.log("ZZZZZZZZZZ:");
						//console.log("YYYYY:"+channel.name);
						//console.log("MESSAGE:"+rrmsg);
						//console.log("MESSAGE:"+rrmsg.content);
						console.log("--------------------------------------------------------------------");
					});
					//rrmsg.reactions.removeAll().catch(error => 
					//	console.error('Failed to clear reactions: ', error)
					//);
					//
				}); 
				
			}
		}
	});
}

//Manually adding voting messages (by sending a message) - for debug purposes
function createVotingMessage(message){
	if(message.author.id == config.votesystem_add_vote_admin_user_id){ //Allow only admin to add new votes
		arrayOfMessage = message.content.split(" ");//Split message into elements divided by spaces
		voteOption = arrayOfMessage.slice(1).join(' ');//join everything except the command (first array element)
		
		
		votingEntry = message.guild.channels.cache.find(ch => ch.id === config.votesystem_channel).send(voteOption).then(sent => {

			let id = sent.id;
			console.log(sent);
			
			const channel = message.guild.channels.cache.find(ch => ch.id === config.votesystem_channel); //voting channel id
			channel.messages.fetch(id).then(rrmsg => {
				sendReactionsToMessage(rrmsg);
				//checkReactions(id);
				//rrmsg.react("♻️"); 	
				//rrmsg.react("1️⃣");
				//rrmsg.react("2️⃣");
				//rrmsg.react("3️⃣");
				//rrmsg.react("4️⃣");
				//rrmsg.react("5️⃣");
				/*
				const { exec } = require('child_process');
				exec('python3 '+config.script_path+config.votesystem_path+'addVotePost.py '+id+'', (err, stdout, stderr) => {
					if (err) { console.log(ReturnDate()+" [ERROR] [CreateVote] id: "+id); }
					else {
						console.log(ReturnDate()+"[INFO] [CreateVote] Added vote post: "+id+ " with vote option: "+voteOption);
					}
				});
				*/
			}); 
		});
		console.log(ReturnDate()+ " [INFO] [CreateVote] Voting entry created.");
		
	}
}

//Adding reactions from array to message --- TODO: support for configfile reactions array
function sendReactionsToMessage(message){
	//console.log(message);
	console.log(ReturnDate()+"[INFO] [sendReactionsToMessage] Triggering reactions for message ID: "+message.id);
	reactionsArray = ["♻️","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣"];
	message.reactions.removeAll().catch(error => console.log(ReturnDate()+' [ERROR] Failed to clear reactions: ', error));
	for(var i = 0; i < reactionsArray.length; i++){
		message.react(reactionsArray[i]);
	}
	
}


function getVotePostsFromDatabase(){	//TODO:Function which gets all voteposts ids from DB and readds reactions
	//con.end();
	//con.connect(function(err) {
	//  if (err) throw err;
	con.query("SELECT * FROM userdata", function (err, result, fields) {//TODO!!
		if (err) throw err;
		//console.log(result);
		for(var i = 0; i < result.length; i++){
			console.log(result[i].discord_username);
		}
	});
	//});
}

///////////////////////////////////////////
////////////////////////// SCHEDULED CRON JOBS
///////////////////////////////////////////
function enableCronJobs(){
	console.log(ReturnDate()+" [INFO] Enabling Cron Jobs");
	// Every thursday at 17:00 and 30 seconds
	
	cron.schedule("00 18 14 * * 4", function(){
		console.log(ReturnDate()+" [INFO] Run schedule - show releases...");
		// fresh releases
		showReleasesImageToChannel("787465529984155658","new");//890640686947381258","new");
		// upcoming releases
		showReleasesImageToChannel("787465529984155658","month");//890640686947381258","month");
	});
	
	
	cron.schedule("00 42 14 * * 4", function(){
		console.log(ReturnDate()+" [INFO] Run schedule - show GLUT...");
		// update tracker
		showGlutImageToChannel("787465529984155658","");//890640686947381258","new");
	});
	
	cron.schedule(config.activity_schedule_cron, function(){
		console.log(ReturnDate()+" [INFO] Run schedule - log Discord activity");
		logActivity();
		logTwitchActivity();
	});
	cron.schedule("0 21 0 * * 2", function(){
		console.log(ReturnDate()+" [INFO] Run schedule - paste activity image");
		pasteActivityImageToChannel(config.activity_image_channel);
	});
	cron.schedule("0 38 20 * * *", function(){
		console.log(ReturnDate()+" [INFO] Run schedule - log Discord member count");
		saveMemberCount();
	});
}
///////////////////////////////////////////
//////////////////////////  LOGIN 
///////////////////////////////////////////
client.login(config.token);
