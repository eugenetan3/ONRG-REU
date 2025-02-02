/*connect to utf8mb4 database, this is the file using now
 *
 *@author: morgan
 *@data created: 6/25/2013
 *@last changed:
 *
 */
import java.net.*;
import java.io.*;
import java.sql.*;
import java.util.*;

import twitter4j.*;
import twitter4j.auth.AccessToken;
import twitter4j.json.DataObjectFactory;
import twitter4j.conf.ConfigurationBuilder;

import com.google.gson.stream.JsonReader;
import com.google.gson.Gson;

public class GetTweet{
    public static DatabaseManager dm_tweet;
    public static DatabaseManager dm_url;
    public static List<String> al_tokens;
    public static List<String> al_ids;

    public static String table_name_tweet;
    public static String table_name_url;

    public static int writeResponseTo(String user_id_str, Twitter twitter, Paging page){
        int counter=0;

        String[] userErrorInfo = new String[2];

        try{
            User user = twitter.showUser(Long.parseLong(user_id_str));  //!!when id, using Long.parseLong; when screen name, use directly
            List<Status> statuses;

            statuses = twitter.getUserTimeline(Long.parseLong(user_id_str), page);//!!when id, using Long.parseLong; when screen name, use directly
            for (int k=0;k<statuses.size();k++) {
                dm_tweet.initMap();			//!!!!!!!!!
                Status status = statuses.get(k);
                counter++;
                //get raw json and parse it
                String rawJSON = DataObjectFactory.getRawJSON(status);
                InputStream in = new ByteArrayInputStream(rawJSON.getBytes("UTF-8"));
                //InputStream in2 = new ByteArrayInputStream(rawJSON.getBytes("UTF-8"));
                JsonReader reader = new JsonReader(new InputStreamReader(in, "UTF-8"));
                //JsonReader reader2 = new JsonReader(new InputStreamReader(in2, "UTF-8"));
                boolean is_retweet = status.isRetweet();
                Tweets tw;
                if( is_retweet ){
                    tw = Tweets.readRetweets(reader);
                    assert(tw != null );
                } else {
                    tw = Tweets.readTweets(reader);
                }
                //System.out.println("tw is :" + tw);

                dm_tweet.mdata.put("tweet_id", String.valueOf(status.getId()) );
                dm_tweet.mdata.put("text", tw.text);   //dm_tweet.mdata.put("text", status.getText());
                dm_tweet.mdata.put("time_created",status.getCreatedAt().toString() );
                boolean is_rep = status.getInReplyToUserId()>0?true:false;
                dm_tweet.mdata.put("is_reply", String.valueOf(is_rep) );//using the value below to evaluate

                //
                //
                boolean is_retweeted = status.isRetweet();
                dm_tweet.mdata.put("is_retweet", String.valueOf(is_retweeted ) );
                if( is_retweeted ){
                    dm_tweet.mdata.put("original_tweet_id", tw.id_str );
                    dm_tweet.mdata.put("original_user_id", tw.user.id_str );
                    dm_tweet.mdata.put("original_screen_name", tw.user.screen_name );
                }
                //System.out.println("here");

                dm_tweet.mdata.put("retweet_count", String.valueOf(status.getRetweetCount()));
                dm_tweet.mdata.put("favorite_count", String.valueOf(tw.favorite_count));//now can do
                dm_tweet.mdata.put("user_id", String.valueOf(user.getId())); userErrorInfo[0] = String.valueOf(user.getId()); userErrorInfo[1] = user.getScreenName();
                dm_tweet.mdata.put("in_reply_to_sid", String.valueOf(status.getInReplyToStatusId()) );
                dm_tweet.mdata.put("in_reply_to_uid", String.valueOf(status.getInReplyToUserId()) );

                dm_tweet.mdata.put("is_truncated", String.valueOf(status.isTruncated()) );
                dm_tweet.mdata.put("is_possibly_sensitive", String.valueOf(status.isPossiblySensitive()) );
                GeoLocation geo = status.getGeoLocation();
                if( geo != null ){
                    double latitude = geo.getLatitude();
                    double longitude = geo.getLongitude();
                    String geo_str = "(" + String.format("%.2f",latitude) + "," + String.format("%.2f",longitude) + ")";
                    dm_tweet.mdata.put("geo_location", geo_str );
                }
                dm_tweet.mdata.put("lang", tw.lang);

                //
                //
                //
                //
                dm_tweet.mdata.put("source", status.getSource());
                dm_tweet.mdata.put("hashtag_count", String.valueOf(tw.entities.hashtags.size()) );
                dm_tweet.mdata.put("user_mention_count", String.valueOf(tw.entities.user_mentions.size()) );
                dm_tweet.mdata.put("url_count", String.valueOf(tw.entities.urls.size()) );



                dm_tweet.mdata.put("time_collected", String.valueOf((new java.util.Date()).getTime()) );

                Set<Integer> skip = new HashSet<Integer>(Arrays.asList(0, 3, 4, 7, 9));

                if( !dm_tweet.mdata.get("tweet_id").equals("") ){
                    String query = "INSERT DELAYED "+table_name_tweet+" (";//\'" + dm_tweet.mdata.get("tweet_id") + "\');";
                    String headers = dm_tweet.sattr[0];
                    String values = "(\'" + dm_tweet.mdata.get(dm_tweet.sattr[0]) + "\'";
                    //System.out.println(query);
                    //dm_tweet.statement.execute(query);
                    for( int i=1;i<dm_tweet.sattr.length;i++ ){
                        if( dm_tweet.mdata.get(dm_tweet.sattr[i]) != null && !dm_tweet.mdata.get(dm_tweet.sattr[i]).equals("") ){//null becomes "" ?
                            headers += ("," + dm_tweet.sattr[i]);

                            if (skip.contains(i)) {
                                values += ("," + dm_tweet.mdata.get(dm_tweet.sattr[i]).replace("\\", "\\\\").replace("'", "\\'") + "");
                            } else {
                                values += (",\'" + dm_tweet.mdata.get(dm_tweet.sattr[i]).replace("\\", "\\\\").replace("'", "\\'") + "\'");
                            }
                            //query = "update tweets set " + dm_tweet.sattr[i] + "=" +  "\'"+dm_tweet.mdata.get(dm_tweet.sattr[i]).replace("\\","\\\\").replace("'","\\'")+"\'" + " where tweet_id =" + dm_tweet.mdata.get("tweet_id");
                            //System.out.println(query);
                            //dm_tweet.statement.execute(query);
                        }
                    }
                    headers += ") ";
                    values += ");";
                    query = query + headers + " values " + values;
                    dm_tweet.statement.execute(query);
                    //System.out.println(dm_tweet.mdata.get(dm_tweet.sattr[0]));
                }

                //url table, now in the end
                //insert the current tweet_id here, not the original
                if( tw.entities.urls.size()>0 ){
                    writeToURLTable(String.valueOf(status.getId()),tw.entities.urls);
                }

            }//for

        } catch (Exception e){
            System.err.println("error in GetTweet:"+ e.getMessage());
            System.err.println("user id: " + userErrorInfo[0] + "\tuser screen name: " + userErrorInfo[1]);
            return counter;
        }

        try{
            ResultSet rs = dm_tweet.statement.executeQuery("select count(*) from "+table_name_tweet);
            rs.next();
            System.out.println("Now there are :" + rs.getObject(1) + " rows in "+table_name_tweet);
        } catch (Exception e){
            System.err.println("error in GetTweet:"+ e.getMessage());
            return counter;
        }
        return counter;
    }



    //insert into url table
    //bad style
    public static void writeToURLTable(String tweet_id, List<String> urls) throws Exception{
        //System.out.println(tweet_id);
        for(int i=0;i<urls.size();i++){
            String query = "INSERT DELAYED "+table_name_url+" values(\'" + tweet_id+ "\'," + "\'"+urls.get(i).replace("\\","\\\\").replace("'","\\'") + "\');";
            dm_url.statement.execute(query);
        }
    }



    public static void start(List<String> l_tokens, List<String> l_ids, String[] tweet_attrs, String[] db_attrs, int num_primary_key, List<String> al_tables, boolean is_collect_hourly) throws Exception{
        al_tokens = l_tokens;
        al_ids = l_ids;
        table_name_tweet = al_tables.get(1);
        table_name_url = al_tables.get(2);

        //String[] tweet_attrs = {"tweet_id", "text", "time_created","is_reply","is_retweet","original_user_id","original_screen_name","retweet_count","favorite_count","user_id","in_reply_to_sid", "in_reply_to_uid","is_truncated","is_possibly_sensitive","geo_location","lang","source","hashtag_count","user_mention_count","url_count","time_collected"};//21
        dm_tweet = new DatabaseManager(db_attrs[0],db_attrs[1],db_attrs[2],db_attrs[3],db_attrs[4],tweet_attrs,num_primary_key );
        dm_tweet.connect();
        dm_tweet.getStatement();
        dm_tweet.initMap();

        String[] tweet_url = {"tweet_id", "url"};//2
        dm_url = new DatabaseManager(db_attrs[0],db_attrs[1],db_attrs[2],db_attrs[3],db_attrs[4],tweet_url,2);
        dm_url.connect();
        dm_url.getStatement();
        dm_url.initMap();


        //String screen_name = "adidas";
        //each token can do 180 pages, so now the number of tokens should be enough

        int i = 0;	//index in the al_tokens
        int counter = 0; // the number of round

        int page_upper_bound;
        if( is_collect_hourly ){ page_upper_bound = 1;}//just collect 1 page per user
        else {page_upper_bound = 20;}	//all pages

        for(int index_id=0;index_id<al_ids.size();index_id++){
            System.out.println("Now doing " + (index_id+1) + "th id, the total is " + al_ids.size());

            //int index = 0;		//the index of al_tokens


            for(int p=1;p<=page_upper_bound;p++){	//1 or 20 pages depending on hourly or not

                Paging page = new Paging(p, 200);
                try{
                    TwitterFactory factory = new TwitterFactory(new ConfigurationBuilder().setJSONStoreEnabled(true).build());
                    Twitter twitter = factory.getInstance();
                    //Twitter twitter = new TwitterFactory().getInstance();
                    String[] tokens = al_tokens.get(i).split(" ");
                    twitter.setOAuthConsumer(tokens[0], tokens[1]);//tokens[0]:consumer token; toknes[1]:consumer secret
                    AccessToken accessToken = new AccessToken(tokens[2], tokens[3]);
                    twitter.setOAuthAccessToken(accessToken);

                    i = (i+1) % al_tokens.size();
                    if( i == 0 ){//a new round
                        counter ++;
                        if(counter == 14){
                            System.out.println("Limit reached! sleep 12 mins!!\nSuspended at " + (new java.util.Date()));
                            Thread.sleep(1000 * 720);
                            counter = 1;
                        }
                    }


                    int count = writeResponseTo(al_ids.get(index_id), twitter, page);
                    System.out.println("the return value is: "+ String.valueOf(count) );
                    if(count ==0) break;// reach the last tweet, so break this loop
                } catch (Exception e){
                    System.err.println("start funciton error in GetTweet:"+ e.getMessage());
                    continue;
                }
            }
            //System.out.println("Sleep for 5 sec for safety");
            //Thread.sleep(1000 * 5);
        }


    }
}
