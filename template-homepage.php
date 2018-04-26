<?php
/*
Template Name: Home Page
*/
?>

<?php get_header(); ?>

		<div class="row" id="banner">
    <img src="<?php bloginfo('template_directory'); ?>/images/sampleBanner.jpg" width="1000" height="268" alt="Banner">
    </div>
  <div class="row mainFrameRightBck" id="mainFrame">
    	<div id="mainCol">
        	<section id="content">
            <header id="pageHeader">
            		<h1>About Us</h1>
            	</header>
                
                <?php while ( have_posts() ) : the_post(); ?>
<?php the_content(); ?>
<?php endwhile; // end of the loop. ?>


            
</section>
        </div><!-- end main content column -->

<?php get_sidebar(); ?>
<?php get_footer(); ?>