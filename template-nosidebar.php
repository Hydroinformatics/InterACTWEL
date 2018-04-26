<?php
/*
Template Name: Full Page (No Sidebar)
*/
?>

<?php get_header(); ?>

		<div class="row" id="mainFrame">
    	<div id="mainCol-full">

<?php while ( have_posts() ) : the_post(); ?>
<?php get_template_part( 'content', get_post_format() ); ?>
<?php endwhile; // end of the loop. ?>
            
</div><!-- end main content column -->


<?php get_footer(); ?>