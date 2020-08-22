/**
 *	The number of the followers should be fewer than 5000*15 = 75000
 *
 * @date created 6/27/2013
 * @last changed
 * @author: morgan
 */
import java.sql.*;
import java.io.*;
import java.util.*;


import com.google.gson.stream.JsonReader;
import com.google.gson.Gson;


import twitter4j.json.DataObjectFactory;
import twitter4j.auth.AccessToken;
import twitter4j.conf.ConfigurationBuilder;
import twitter4j.*;

public class GetFollowers{
	public static DatabaseManager dm;
	
	public static List<String> al_tokens;
	public static List<String> al_ids;
	
	public static String table_name_fr_fo;
	
	
	/*
	 *	If there are fewer than 3000, then return them all.
	 * Otherwise return 3000 from the original list
	 */
	public static List<Long> getRandom3000(List<Long> al_follower_ids){
		if(al_follower_ids.size() <= 3000){
			return al_follower_ids;
		} else {
			List<Long> al_random_3000 = new ArrayList<Long>();
			
			long size = al_follower_ids.size();
			List<Integer> al_indices = new ArrayList<Integer>();
			for(int i=0;i<size;i++){
				al_indices.add(i);
			}
			
			
			Random rd = new Random();
			while(al_random_3000.size() < 3000){
				int index_in_new = Math.abs(rd.nextInt()) % al_indices.size();
				int index_in_original = al_indices.get(index_in_new);
				long id = al_follower_ids.get(index_in_original);
				al_random_3000.add(id);
				
				//System.out.println("the size of al_random_25 is " + al_random_25.size());
				al_indices.remove(index_in_new);//remove that element	
						
			}
			
			return al_random_3000;
		}
		
	}
	
	
	public static boolean writeResponseTo(String user_id_str, List<Long> al_follower_ids){
		try{
			
			//List<Long> al_random_3000 = getRandom3000(al_follower_ids);
            List<Long> al_random_3000 = al_follower_ids;

			for(int i=0;i<al_random_3000.size();i++){
				String query = "INSERT DELAYED "+table_name_fr_fo +" values(\'" + user_id_str+ "\'," + "\'"+ String.valueOf(al_random_3000.get(i))+ "\');";
				dm.statement.execute(query);

			}	
										
		} catch (SQLException sqle){
			System.err.println("sqlError in GetFollowers::"+ sqle.getMessage());		
			return true;//////////////////////////////////////!!!!!!
		} catch (Exception e){//this should not apply in this friend_follower database
			String error_str = e.getMessage();
			System.err.println("error in GetFollowers::"+ error_str);
			if(error_str.startsWith("404")){return true;}//if no this user returns true
			else if(error_str.startsWith("403")){return true;}//The request is understood, but
			else{return false;}
		}
		
		try{
			ResultSet rs = dm.statement.executeQuery("select count(*) from "+table_name_fr_fo);
			rs.next();
			System.out.println("Now there are :" + rs.getObject(1) + " in friend_follower.");
		} catch (Exception e){
			System.err.println("error in GetFollowers:"+ e.getMessage());
			return false;
		}
		return true;
	}
	
	

	//bad style
	public static void start(List<String> l_tokens, List<String> l_ids, String[] ff_attrs, String[] db_attrs, int num_primary_key, List<String> al_tables) throws Exception{		
		al_tokens = l_tokens;
		al_ids = l_ids;
		table_name_fr_fo = al_tables.get(3);	//the 4th parameter in the db_info file
		
		//String[] attrs = {"friend_id","follower_id"};
		dm = new DatabaseManager(db_attrs[0],db_attrs[1],db_attrs[2],db_attrs[3],db_attrs[4],ff_attrs,num_primary_key);		
		dm.connect();
		dm.getStatement();
		dm.initMap();
		
		
		
		int index_token = 0;
		for(int index_id=0; index_id<al_ids.size(); index_id++){
			System.out.println("now doing " + (index_id +1) + "th, out of "+ al_ids.size());
		
			Twitter twitter = new TwitterFactory().getInstance();
			String[] tokens = al_tokens.get(index_token).split(" ");
			twitter.setOAuthConsumer(tokens[0], tokens[1]);//tokens[0]:consumer token; toknes[1]:consumer secret
			AccessToken accessToken = new AccessToken(tokens[2], tokens[3]);
			twitter.setOAuthAccessToken(accessToken);
					
			List<Long> al_follower_ids = new ArrayList<Long>();
			long cursor = -1;
	      IDs ids;
			int count = 0;	//seems not being used
			
//new 	
			int token_round = 0;
			int per_token_count=0;	
	      do {
				if(per_token_count == 14){ //limit reached, then to go the next token
					index_token++;
					System.out.println("token index now is: "+ index_token);
					tokens = al_tokens.get(index_token).split(" ");
					twitter = new TwitterFactory().getInstance();
					twitter.setOAuthConsumer(tokens[0], tokens[1]);
					accessToken = new AccessToken(tokens[2], tokens[3]);
					twitter.setOAuthAccessToken(accessToken);
					per_token_count = 0;
				}
			
	         ids = twitter.getFollowersIDs(Long.parseLong(al_ids.get(index_id)), cursor);
				per_token_count++;
	         for (long id : ids.getIDs()) {		 		
					al_follower_ids.add(id);
	         }
	      } while ((cursor = ids.getNextCursor()) != 0);
			System.out.println("the num of folloers is :" + al_follower_ids.size());
			writeResponseTo(al_ids.get(index_id),al_follower_ids);
			

			if(index_token == al_tokens.size()-1){
				System.out.println("Limit reached! sleep 15 mins!!\nSuspended at " + (new java.util.Date()));
				Thread.sleep(1000 * 900);
				index_token = -1;
			}
			
			index_token++;
		}
	}
}