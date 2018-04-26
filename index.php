<?php
/**
 * The main template file.
 */

get_header(); ?>

		<div class="row mainFrameRightBck" id="mainFrame">
    	<div id="mainCol">

			<?php if ( have_posts() ) : ?>

				<?php /* Start the Loop */ ?>
				<?php while ( have_posts() ) : the_post(); ?>

					<?php get_template_part( 'content', get_post_format() ); ?>

				<?php endwhile; ?>

			<?php else : ?>

				<section id="content">
                
				
                <header id="pageHeader"><h1><?php _e( 'Not Found' ); ?></h1></header>

				<p><?php _e( 'Sorry, but you are looking for something that is not here. Please try again.' ); ?></p>
					
				
                </section>

			<?php endif; ?>
            
</div><!-- end main content column -->

<?php get_sidebar(); ?>
<?php get_footer(); ?>