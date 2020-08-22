/*
 * Copyright 2007 Yusuke Yamamoto
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

//package twitter4j.examples.json;

import twitter4j.Status;
import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.json.DataObjectFactory;
import twitter4j.auth.AccessToken;
import twitter4j.conf.ConfigurationBuilder;

import java.io.*;
import java.util.List;
import java.util.*;
import twitter4j.*;

import com.google.gson.stream.JsonReader;
import com.google.gson.Gson;
/**
 * Example application that gets public timeline and store raw JSON strings into statuses/ directory..<br>
 *
 * @author Yusuke Yamamoto - yusuke at mac.com
 */
public final class SaveRawJSON {
    /**
     * Usage: java twitter4j.examples.json.SaveRawJSON
     *
     * @param args String[]
     */
    public static void main(String[] args) throws TwitterException {
	 		TwitterFactory factory = new TwitterFactory(new ConfigurationBuilder().setJSONStoreEnabled(true).build()); 
        	Twitter twitter = factory.getInstance();
			twitter.setOAuthConsumer("rj5kOFoZ0MxswunoBLXww", "7UnIGqQzjaH0Z7gjsUQcYQzbNQUAqRJeWgk2zFbk");
			String token = "1398663810-YiozQ2SshDs6Ula9v5y4b0Jec85w7fXilXAwXc7";
			String tokenSecret = "NiBwoxp7j9Qr8PSqcZ0UbBLuMB9zgIU6AGZnVF2QVNbtK";
			AccessToken accessToken = new AccessToken(token, tokenSecret);
			twitter.setOAuthAccessToken(accessToken);

	//!!!!		
			/*IDs ids = twitter.getFriendsIDs(300114634, -1);
			long[] idss = ids.getIDs();
			System.out.println(idss.length);
			for(int k=0;k<idss.length;k++){
				//System.out.println(idss[k]);
			}*/

	//!!!!			
			//IDs ids = twitter.getFollowersIDs(300114634, -1);
			//long[] idss = ids.getIDs();
			/*User u1 = null ;
     		long cursor = -1;
	      IDs ids;
			int count = 0;
	      System.out.println("Listing followers's ids.");
	      do {
						//System.out.println("cursor is :" + cursor);
	              ids = twitter.getFollowersIDs("GoDucks", cursor);
	          for (long id : ids.getIDs()) {
				 		count++;
	//time rate should be added here
	              //System.out.println(id);
	              //User user = twitter.showUser(id);
	              //System.out.println(user.getName());
	          }
	      } while ((cursor = ids.getNextCursor()) != 0);
			System.out.println(count);
		*/
		
		//get user id test, two lines
		//User user = twitter.showUser(1352034954);
		//System.out.println(user.getScreenName());
		
			//System.out.println(idss.length);
       
		  //System.out.println("Saving public timeline.");
        try {
            new File("statuses3").mkdir();
            List<Status> statuses = twitter.getUserTimeline("StateDept");
            for (Status status : statuses) {
                String rawJSON = DataObjectFactory.getRawJSON(status);
                String fileName = "statuses3/" + status.getId() + ".json";
                storeJSON(rawJSON, fileName);
					 System.out.println(rawJSON);
		/*			 
		InputStream in = new ByteArrayInputStream(rawJSON.getBytes("UTF-8"));
	  	JsonReader reader = new JsonReader(new InputStreamReader(in, "UTF-8"));
		
		
		//twitter.showUser("Nike");
		Map<String,RateLimitStatus> m = twitter.getRateLimitStatus();
		Set<String> s = m.keySet();
		//for(String key : s){
		//	System.out.println(key);
		//}
		RateLimitStatus rls1 = m.get("/statuses/user_timeline");
		RateLimitStatus rls2 = m.get("/users/show/:id");
		System.out.println("the remaining user_timeline is:" + String.valueOf(rls1.getRemaining()) );
		System.out.println("the remaining /users/show/:id is:" + String.valueOf(rls2.getRemaining()) );
		Tweets tw = Tweets.readTweets(reader);
		System.out.println(tw.favorite_count);
		//ReTweets rtw = ReTweets.readReTweets(reader);
		//System.out.println(rtw.tw.favorite_count);
		*/			 
                //System.out.println(fileName + " - " + status.getText());
            }
            System.out.print("\ndone.");
            System.exit(0);
        } catch (IOException ioe) {
            ioe.printStackTrace();
            System.out.println("Failed to store tweets: " + ioe.getMessage());
        } catch (TwitterException te) {
            te.printStackTrace();
            System.out.println("Failed to get timeline: " + te.getMessage());
            System.exit(-1);
        }
    }

    private static void storeJSON(String rawJSON, String fileName) throws IOException {
        FileOutputStream fos = null;
        OutputStreamWriter osw = null;
        BufferedWriter bw = null;
        try {
            fos = new FileOutputStream(fileName);
            osw = new OutputStreamWriter(fos, "UTF-8");
            bw = new BufferedWriter(osw);
            bw.write(rawJSON);
            bw.flush();
        } finally {
            if (bw != null) {
                try {
                    bw.close();
                } catch (IOException ignore) {
                }
            }
            if (osw != null) {
                try {
                    osw.close();
                } catch (IOException ignore) {
                }
            }
            if (fos != null) {
                try {
                    fos.close();
                } catch (IOException ignore) {
                }
            }
        }
    }
}
