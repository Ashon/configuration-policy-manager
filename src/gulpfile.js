var gulp = require('gulp');
var gutil = require('gulp-util');
var shell = require('gulp-shell');
var jasmine = require('gulp-jasmine-node');
var watch = require('gulp-watch');
var wait = require('gulp-wait');


gulp.task('frisby-jasmine-node-test', shell.task([
    'jasmine-node jasmine/ --color'
]));

gulp.task('python-django-nose-test', shell.task([
   'nosetests'
]));


gulp.task('watch-python', [
        'python-django-nose-test'
    ], function() {
        gulp.watch([
            './*.py',
            './tests/*.py',
        ], [
            'python-django-nose-test',
        ]);

    }
);


gulp.task('watch-frisby', ['frisby-jasmine-node-test'], function(cb) {
        gulp.watch([
            './*.py',
            './tests/*.py',
            './jasmine/*.js'
        ], function(e) {
            gulp
                .src(e.path)
                .on('end', function() { gutil.log('files changed. api test will starts within 2 seconds...') })
                .pipe(wait(2000))
                .pipe(shell('jasmine-node jasmine/ --color'))
                .on('end', function() { gutil.log('api test ended. keep watching...') })
        });
    }
);


gulp.task('default', [
    'python-django-nose-test',
    'watch-python',
    'watch-frisby'
]);
