"""
Contains all the required overhead logic required
to run the program and set things up for the
modules.
This will be the file that is run by the user.
"""
import file_handling
import environment

def main():
    grade_book = file_handling.GradeBook("/home/zen/Downloads/gradebook_11414.201710_Lab203_2016-10-02-14-50-15.zip")
    if not grade_book.already_extracted():
        print("WALDJAWKJDALWKJDLAWKJDLK")
        grade_book.extract_all_attempts()
    grade_book.process_all_attempts()
    environment.TAinator(grade_book.attempts).run()


if __name__ == "__main__":
    main()
