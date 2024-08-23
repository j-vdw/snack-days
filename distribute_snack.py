#!/usr/bin/python3.8

"""
Copyright (c) 2024 Jorgen Vandewoestijne. All Rights reserved
"""

import optparse
from datetime import date, timedelta
from math import ceil
import logging

# indicate approximate length of summer vacation (must be greater than or equal to effective duration)
SUMMER_LENGTH = 60

def count_occurence(tuple_list, keep_indices=False):
   # count the number of times the second element of a tuple is present in the tuple list
   # returns tuple (number occurences, indices where they occur (only last by default), ???)

   occurences = {}
   for i, value in enumerate(tuple_list):
      if value[1] in occurences:
         occurences[value[1]] = (occurences[value[1]][0] + 1, occurences[value[1]][1] + [i] if keep_indices else [i], min(abs(i - occurences[value[1]][1][-1]),occurences[value[1]][2]))
      else:
         occurences[value[1]] = (1, [i], 1000)
   logging.info(occurences)
   return occurences

def move_bdays(bday_dates, vacation_dates, all_before=False):
   # move bdays before or after vacation dates based on if they are before or after half of the vacation,
   #   only before if the vacation is only one week
   # bday_dates =  list of tuples (date, name) where date is in iso format - '2021-09-05', dates can be missing
   mid_vacation = int(len(vacation_dates)/2) if len(vacation_dates) > 9 else len(vacation_dates) - 1
   bday_dates_dict = dict(bday_dates)
   n = 0
   bday_dates_keys = list(bday_dates_dict.keys())
   last_school_day_index = bday_dates_keys.index(vacation_dates[0]) - 1
   first_school_day_index = bday_dates_keys.index(vacation_dates[-1]) + 1
   for vacation_date in vacation_dates[-1::-1] if all_before else vacation_dates[mid_vacation::-1]:
      if bday_dates_dict[vacation_date]:
         while bday_dates[last_school_day_index - n][1]:
            n += 1
         bday_dates[last_school_day_index - n] = (bday_dates[last_school_day_index - n][0], bday_dates_dict[vacation_date])
         logging.info('bday found: ' + vacation_date + '. It will be placed in front on: ' + bday_dates[last_school_day_index - n][0])
         n += 1
   if len(vacation_dates) > 9 and not all_before:
      n = 0
      for vacation_date in vacation_dates[mid_vacation + 1:]:
         if bday_dates_dict[vacation_date]:
            while bday_dates[last_school_day_index + n][1]:
               n += 1
            bday_dates[first_school_day_index + n] = (bday_dates[first_school_day_index + n][0], bday_dates_dict[vacation_date])
            logging.info('bday found in second half: ' + vacation_date +  '. It will be placed in front on: ' + bday_dates[last_school_day_index + n][0])
            n += 1
   del bday_dates[last_school_day_index + 1:first_school_day_index]
   return bday_dates

def find_date(snack_dates, name, index, delta=1, max_delta=6):
   # snack_dates : list of tuples (date, name) where date is in iso format - '2021-09-05', dates can be missing
   # index : index where new name is ideally placed
   # delta : distance from ideal index which should be tried
   # max_delta : max distance from ideal index which is allowed
   date_ok = 0
   logging.info('Trying delta ' + str(delta) + ' around date ' + snack_dates[index][0])
   if delta > max_delta:
      logging.error('no date found around ' + snack_dates[index][0])
      return snack_dates
   if (index + delta < len(snack_dates)):
      logging.info('trying index ' + str(index + delta))
      if not snack_dates[index + delta][1] :
         snack_dates[index + delta] = (snack_dates[index + delta][0], name)
         date_ok = 1
   if not date_ok and (index - delta >= 0):
      logging.info('trying index ' + str(index - delta))
      if not snack_dates[index - delta][1]:
         snack_dates[index - delta] = (snack_dates[index - delta][0], name)
         date_ok = 1
   if not date_ok:
      snack_dates = find_date(snack_dates, name, index, delta + 1)
   return snack_dates

def generate_snack_calendar(bdays, school_year, all_saints, winter, spring, easter, homedays):

   bdays_in_summer = 0
   bdays.sort() # sorting occurs on first element of tuple

   # step 1: create list with all dates of the year. The item corresponding to a birthday will have a tuple with the name of the person.
   start_date = date.fromisoformat(school_year[0])
   end_date = date.fromisoformat(school_year[1]) + timedelta(days=SUMMER_LENGTH)
   date_range = dict([((start_date + timedelta(days=i)).isoformat(), None) for i in range((end_date - start_date).days + 1)])
   #   Place bdays
   for bday, name in bdays:
      if not date_range[bday]:
         date_range[bday] = name
      else:
         logging.error('2 birthdays on same date') # not handled yet
   date_range = list(date_range.items()) # transform to list for easier manipulation
   logging.info("step 1:")
   # step 2: move birthdays outside non-school days (and remove non-school days)
   # - weekend, summer holidays: move before (unless day already taken by another birthday)
   # - all_saints, winter, spring, easter holidays: bdays in first half are before, bdays in second half are after (unless only a week)
   logging.info('checking summer birthdays')
   vacation = [(date.fromisoformat(school_year[1]) + timedelta(days=1) + timedelta(days=i)).isoformat() for i in range(60)]
   date_range = move_bdays(date_range, vacation, all_before=True)
   count_occurence(date_range)
   logging.info('checking all saints birthdays')
   vacation = [(date.fromisoformat(all_saints[0]) + timedelta(days=i)).isoformat() for i in range((date.fromisoformat(all_saints[1]) - date.fromisoformat(all_saints[0])).days + 1)]
   date_range = move_bdays(date_range, vacation)
   count_occurence(date_range)
   logging.info('checking winter birthdays')
   vacation = [(date.fromisoformat(winter[0]) + timedelta(days=i)).isoformat() for i in range((date.fromisoformat(winter[1]) - date.fromisoformat(winter[0])).days + 1)]
   date_range = move_bdays(date_range, vacation)
   count_occurence(date_range)
   logging.info('checking spring birthdays')
   vacation = [(date.fromisoformat(spring[0]) + timedelta(days=i)).isoformat() for i in range((date.fromisoformat(spring[1]) - date.fromisoformat(spring[0])).days + 1)]
   date_range = move_bdays(date_range, vacation)
   count_occurence(date_range)
   logging.info('checking easter birthdays')
   vacation = [(date.fromisoformat(easter[0]) + timedelta(days=i)).isoformat() for i in range((date.fromisoformat(easter[1]) - date.fromisoformat(easter[0])).days + 1)]
   date_range = move_bdays(date_range, vacation)
   count_occurence(date_range)
   logging.info('checking weekends and homedays')
   # weekends/homedays are removed by creating a new date_range list and only adding valid schooldays.
   # while constructing the new list, birthdays in weekend/homeday are moved
   date_range_new = []
   names_to_move = []
   for i, date_tuple in enumerate(reversed(date_range)):
      day_index = date.fromisoformat(date_tuple[0]).weekday()
      # logging.info('checking ' + date_tuple[0])
      if (day_index in [5,6]) or (date_tuple[0] in homedays):
         if date_tuple[1]: # if a bday is in the weekend, move it before. 2 bdays in a weekend not yet handled
            logging.debug("weekend/homedays: found: " + date_tuple[1])
            names_to_move = names_to_move + [date_tuple[1]]
      else:
         if len(names_to_move):
            if not(date_tuple[1]):
               date_tuple = (date_tuple[0], names_to_move.pop(0))
         logging.debug(str(date_tuple) + " is placed on index " + str(day_index))
         date_range_new = [date_tuple] + date_range_new
   date_range = date_range_new.copy()
   count_occurence(date_range)
   logging.info("step 3:")
   # check placement of all students
   index_dict = {}
   index_dict_mod = {}
   for i, date_tuple in enumerate(date_range):
      if date_tuple[1]:
         index_dict[date_tuple[1]] = i
         index_dict_mod[date_tuple[1]] = (i, i %len(bdays))
   index_list_mod = sorted(list(index_dict_mod.items()), key=lambda tup: tup[1][1])
   print(*index_list_mod, sep="\n")
   # correct 'initial index' in order to have evenly distributed indices (created manually based on index_dict_mod above)
   logging.debug("This step still needs to be done manually: based on the\n \
                  index_list found, add a correction factor to ensure the \n \
                  indices are uique and go from 0 to the number of \n \
                  students - 1.")
   import pdb; pdb.set_trace()
   correction_dict = {'Aaa': -3, 'Bbb': -3, 'Ccc': -3, 'Ddd': -5, 'Eee': -5, 'Fff': -5, 'Ggg': -5, 'Hhh': -5, 'Iii': -4, 'Jjj': -3, 'Kkk': -4, 'Lll': -4, 'Mmm': -3, 'Nnn': -3, 'Ooo': -2, 'Ppp': -1, 'Qqq': -1, 'Rrr': -1, 'Sss': 0, 'Ttt': 0, 'Uuu': -1, 'Vvv': -1, 'Www': -1}
   for i, (kid, index_mod) in enumerate(index_list_mod):
      print(kid + " " + str(i - index_mod[1]))
      correction_dict.update({kid: i - index_mod[1]})
   print("Each kid should now have their unique index")
   for kid in correction_dict:
      index_dict_mod[kid] = (index_dict_mod[kid][1] + correction_dict[kid])%len(bdays)
   index_list_mod = sorted(list(index_dict_mod.items()), key=lambda tup: tup[1])
   print(*index_list_mod, sep="\n")
   # Start from initial placement, distribute evenly, do not assign when there is a conflict
   conflict_slots = {}
   max_slots = ceil(len(date_range)/len(bdays))
   for kid, bday_slot in reversed(index_dict.items()):
      nb_slots = 1 # start at 1 as birthday is already encoded
      logging.info(kid + " : " + str(bday_slot))
      test_slot = bday_slot + correction_dict[kid]
      # Assign slots after birthday
      while (test_slot < len(date_range) - len(bdays)) and (nb_slots < max_slots):
         test_slot += len(bdays)
         if not date_range[test_slot][1]:
            date_range[test_slot] = (date_range[test_slot][0], kid)
            nb_slots = nb_slots + 1
         else:
            if kid in conflict_slots:
               conflict_slots[kid] = conflict_slots[kid] + [test_slot]
            else:
               conflict_slots[kid] = [test_slot]
      # Assign slots before birthday
      test_slot = bday_slot + correction_dict[kid]
      while (test_slot >= 0 + len(bdays)) and (nb_slots < max_slots):
         test_slot -= len(bdays)
         if not date_range[test_slot][1]:
            date_range[test_slot] = (date_range[test_slot][0], kid)
            nb_slots = nb_slots + 1
         else:
            if kid in conflict_slots:
               conflict_slots[kid] = conflict_slots[kid] + [test_slot]
            else:
               conflict_slots[kid] = [test_slot]
   noconflict_result = sorted(list(count_occurence(date_range).items()), key=lambda tup: tup[1][0])
   print("Current number of slots assigned \n")
   for kid, cnt in noconflict_result:
      print(("None" if kid == None else kid) + " : " + str(cnt[0]))
   # Try to assign remaining slots (starting with kids having the least assigned slots)
   for kid, unused in noconflict_result:
      if kid in conflict_slots:
         for slot in conflict_slots[kid]:
            date_range = find_date(date_range, kid, slot, max_delta=10)
   conflict_result = sorted(list(count_occurence(date_range).items()), key=lambda tup: tup[1][0])
   print("Number of slots assigned after trying to shift dates")
   for kid, cnt in conflict_result:
      print(("None" if kid == None else kid) + " : " + str(cnt[0]))
   logging.info('check if all slots are assigned')
   logging.debug("This step still needs to be done manually: check the slots\n \
                 which have not been assigned and assign manually.")
   import pdb; pdb.set_trace()
   if not conflict_result[0][0]:
      logging.info('some slots not assigned :-( => found manually (but not ideal dates)')
      # to be continued:
      # 1) establish list with students having least number of collations
      # 2) determine the one whose closest slot is furthest away among these
      # 3) add missing slot(s)
      date_range[92] = (date_range[92][0],'Ppp')
      date_range[165] = (date_range[165][0],'Nnn')

   conflict_result_man = sorted(list(count_occurence(date_range).items()), key=lambda tup: tup[1][0])
   print("Number of slots assigned after manually adding dates")
   for kid, cnt in conflict_result_man:
      print(("None" if kid == None else kid) + " : " + str(cnt[0]))

   # write results to file
   with open('dates_collation.auto.txt','w') as f:
      for days in date_range:
         f.write(days[0] + ": " + ("None" if days[1] == None else days[1]) + "\n")
   reworked_result = count_occurence(date_range)

if __name__ == "__main__":
  # Parse command line arguments
  parser = optparse.OptionParser()
  parser.add_option("--bdays", help = "tuple list of birthdays with names. ex: [('2021-07-18', 'Aba'), ('2021-11-13', 'Bcb')]", \
                                                                     default = [('2024-09-10', 'Hhh'), \
                                                                                ('2025-01-16', 'Iii'), \
                                                                                ('2025-02-13', 'Ddd'), \
                                                                                ('2025-04-03', 'Fff'), \
                                                                                ('2025-03-14', 'Ttt'), \
                                                                                ('2024-09-24', 'Vvv'), \
                                                                                ('2025-06-29', 'Jjj'), \
                                                                                ('2025-07-03', 'Ppp'), \
                                                                                ('2024-10-23', 'Nnn'), \
                                                                                ('2024-11-03', 'Rrr'), \
                                                                                ('2024-09-14', 'Lll'), \
                                                                                ('2025-03-16', 'Sss'), \
                                                                                ('2025-04-13', 'Ooo'), \
                                                                                ('2025-07-14', 'Mmm'), \
                                                                                ('2025-02-26', 'Kkk'), \
                                                                                ('2024-08-31', 'Bbb'), \
                                                                                ('2025-08-05', 'Qqq'), \
                                                                                ('2024-11-29', 'Ggg'), \
                                                                                ('2025-04-22', 'Uuu'), \
                                                                                ('2024-09-25', 'Www'), \
                                                                                ('2025-06-24', 'Eee'), \
                                                                                ('2025-02-09', 'Aaa'), \
                                                                                ('2025-05-16', 'Ccc')])
  parser.add_option("--homedays", help = "list of non-weekend and non-vacation days where there is no school. ex: ['2021-07-18', '2021-11-13']", \
                                                                     default = ['2024-09-27', \
                                                                                '2024-11-11', \
                                                                                '2024-11-15', \
                                                                                '2025-01-20', \
                                                                                '2025-04-21', \
                                                                                '2025-04-22', \
                                                                                '2025-05-29', \
                                                                                '2025-06-09'])
  parser.add_option('--school_year', help = "first and last date of schoolyear. ex: ['2022-08-29', '2024-07-07']", default = ['2024-08-26', '2025-07-04'])
  parser.add_option('--all_saints', help = "first and last date of all saints holiday. ex: ['2022-10-22', '2022-11-06']", default = ['2024-10-19', '2024-11-03'])
  parser.add_option('--winter', help = "first and last date of winter holiday. ex: ['2022-12-24', '2024-01-08']", default = ['2024-12-21', '2025-01-05'])
  parser.add_option('--spring', help = "first and last date of spring holiday. ex: ['2024-02-18', '2024-03-05']", default = ['2025-02-22', '2025-03-09'])
  parser.add_option('--easter', help = "first and last date of easter holiday. ex: ['2024-04-29', '2024-05-14']", default = ['2025-04-26', '2025-05-11'])
  parser.add_option("--logging_level", "-l", dest="logging_level", default="info", choices=["error","warning", "info","debug"],
                   help="Logging level (error, warning, info, debug)")

  (options, args) = parser.parse_args()
  ########################################################################
  # Set up logging (does nothing if the root logger already has handlers configured for it)
  ########################################################################
  if options.logging_level=="info":
     logging_level=logging.INFO
  elif options.logging_level=="debug":
     logging_level=logging.DEBUG
  elif options.logging_level=="warning":
     logging_level=logging.WARNING
  elif options.logging_level=="error":
     logging_level=logging.ERROR
  logging.basicConfig(level = logging_level)

  generate_snack_calendar(options.bdays, options.school_year, options.all_saints, options.winter, options.spring, options.easter, options.homedays)



