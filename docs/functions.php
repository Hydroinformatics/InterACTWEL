<?php
	
	// Add RSS links to <head> section
	automatic_feed_links();
	
	// Load jQuery
	if ( !is_admin() ) {
	   wp_deregister_script('jquery');
	   wp_register_script('jquery', ("http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"), false);
	   wp_enqueue_script('jquery');
	}
	
	// Clean up the <head>
	function removeHeadLinks() {
    	remove_action('wp_head', 'rsd_link');
    	remove_action('wp_head', 'wlwmanifest_link');
    }
    add_action('init', 'removeHeadLinks');
    remove_action('wp_head', 'wp_generator');
    
	//grabbing the names of the 	
	//add_action("gform_post_submission", "set_post_content", 10, 2);
 	//	function set_post_content($entry, $form){
 		//Gravity Forms has validated the data
 		//Our Custom Form Submitted via PHP will go here
 
		 // Lets get the IDs of the relevant fields and prepare an email message
	//	 $message = print_r($entry, true);
 
 		// In case any of our lines are larger than 70 characters, we should use wordwrap()
 	//	$message = wordwrap($message, 70);
 
		 // Send
	//	 mail('jeynon@iupui.edu', 'Getting the Gravity Form Field IDs', $message);
	// }
	 
	 
	 //Writing to the table to add to the users table/////////////////////////////
	 add_action("gform_post_submission", "set_post_content", 10, 2);
 		function set_post_content($entry, $form){
			
		 $message = print_r($entry, true);
 
 		 //In case any of our lines are larger than 70 characters, we should use wordwrap()
 		$message = wordwrap($message, 70);
 
		 // Send
	    mail('jeynon@iupui.edu', 'Getting the Gravity Form Field IDs', $message);
 
 		// Lets get the IDs of the relevant fields and prepare an email message
 		//$message = print_r($entry, true);
 
 		// In case any of our lines are larger than 70 characters, we should use wordwrap()
 		//$message = wordwrap($message, 70);
 
 		// Send
 		//mail('travis@0to5.com', 'Getting the Gravity Form Field IDs', $message);
 
 		function post_to_url($url, $data) {
		 $fields = '';
		 foreach($data as $key => $value) {
		 $fields .= $key . '=' . $value . '&';
		 }
 		rtrim($fields, '&');
 
 		$post = curl_init();
 
 		curl_setopt($post, CURLOPT_URL, $url);
 		curl_setopt($post, CURLOPT_POST, count($data));
		 curl_setopt($post, CURLOPT_POSTFIELDS, $fields);
 		curl_setopt($post, CURLOPT_RETURNTRANSFER, 1);
 
		 $result = curl_exec($post);
 
	 curl_close($post);
	 }
 
 		if($form["id"] == 1){//Join Our Mailing List
 
 		$data = array(
		// "Password" =>     $entry["38"],
		// "User_Name" =>     $entry["36"],
		// "Email_ID" =>         $entry["35"],
		 
		"FNAME" => $entry["34.3"],
		"LNAME" => $entry["34.6"],
		"EMAIL" => $entry["35"],
		"USERNAME" => $entry["36"],
		"PASSWORD" => $entry["38"],
		"TENURE" => $entry["3"],
		"SUBBASIN_OWN_FARM" => $entry["4"],
		"SUBBASIN_FARM_CROP" => $entry["5"],
		"SUBBASIN_FARM_CASH" => $entry["6"],
		"CROP_KINDS" => $entry["7"],
		"CROP_FARMING_DURATION" => $entry["8"],
		"INTERESTED_FARMBILL" => $entry["10"],
		"INTERESTED_PROGRAMS" => $entry["11.1"],
		"BMP" => $entry["12.1"],
		//"BMP" => $entry["12.1"] . ',' . $entry["12.2"] . ',' . $entry["12.3"] . ',' . $entry["12.4"] . ',' . $entry["12.5"] . ',' . $entry["12.6"] . ',' . $entry["12.7"] . ',' . $entry["12.8"] . ',' . $entry["12.9"] . ',' . $entry["12.11"],
		"CHOSENFF" => $entry["13.2"],
		"PRACTICE_SATISFY" => $entry["15"],
		"PRACTICE_FLOODING" => $entry["16"],
		"PRACTICE_FERTILIZER" => $entry["17"],
		"PRACTICE_SOILEROSION" => $entry["18"],
		"PRACTICE_SOILHEALTH" => $entry["19"],
		"BENEFIT_PROGRAMINCENTIVE" => $entry["20"],
		"BENEFIT_PRODUCTIVITY" => $entry["21"],
		"BENEFIT_RENT" => $entry["22"],
		"MOTIVES" => $entry["42"],
		"FERTILIZERUSE" => $entry["24"],
		"PESTICIDEUSE" => $entry["25"],
		"AVERAGEYIELD" => $entry["26"],
		"BESTCORNYIELD" => $entry["27"],
		"WORSTCORNYIELD" => $entry["28"],
		"BESTSOYBEANYIELD" => $entry["29"],
		"WORSTSOYBEANYIELD" => $entry["30"],
		"INCOMESOURCE_FARMING" => $entry["31"]
		 
		 //"company" =>     $entry["3"],
		// "street" =>         $entry["4.1"],
		// "city" =>         $entry["4.3"],
 		//"state" =>         $entry["4.4"],
 		//"zip" =>         $entry["4.5"],
 		//"country" =>     $entry["4.6"],
		// "website" =>     $entry["10"],
		// "email" =>         $entry["5"],
		// "phone" =>         $entry["6"],
 		///"industry" =>     $entry["7"],
		// "description" => $entry["8"],
		// "formName" => "join-mailing-list-98368402345"
 		);
		//echo $data;
 
		 post_to_url("http://wrestore.iupui.edu/model/takeGFdata.php", $data);
 
	 }
 
 }
	 

?>

<?php
if (function_exists('register_sidebar')) {
	register_sidebar(array(
		'name'=> 'Featured Links',
		'id' => 'featuredlinks',
		'before_widget' => '',
        'after_widget' => '',

	));

}
?>